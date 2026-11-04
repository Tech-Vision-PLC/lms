# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

import re

import requests

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


ADMIN_ROLES = {"System Manager", "Moderator"}
BANK_DETAIL_FIELDS = ("account_name", "business_name", "bank_code", "account_number")
SUBACCOUNT_URL = "https://api.chapa.co/v1/subaccount"
BANKS_URL = "https://api.chapa.co/v1/banks"
SUBACCOUNT_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,128}$")


class LMSTeacherPayoutAccount(Document):
	def validate(self):
		self.validate_owner()
		self.reset_setup_after_bank_change()
		self.validate_setup()

	def validate_owner(self):
		if is_payout_admin():
			return

		if self.is_new():
			if self.teacher and self.teacher != frappe.session.user:
				frappe.throw(_("You can only create payout details for your own account."))
			self.teacher = frappe.session.user
			return

		if self.teacher != frappe.session.user:
			frappe.throw(_("You can only update your own payout details."))

		for field in (
			"chapa_subaccount_id",
			"payout_account_status",
			"split_type",
			"split_value",
			"setup_error",
			"verified_on",
			"verified_by",
		):
			if self.has_value_changed(field):
				frappe.throw(_("Only an administrator can change Chapa setup fields."))

	def reset_setup_after_bank_change(self):
		if self.is_new() or not any(self.has_value_changed(field) for field in BANK_DETAIL_FIELDS):
			return

		self.chapa_subaccount_id = None
		self.payout_account_status = "Pending Verification"
		self.setup_error = None
		self.verified_on = None
		self.verified_by = None

	def validate_setup(self):
		if self.chapa_subaccount_id and frappe.db.exists(
			"LMS Teacher Payout Account",
			{"chapa_subaccount_id": self.chapa_subaccount_id, "name": ["!=", self.name]},
		):
			frappe.throw(_("This Chapa subaccount is already linked to another seller."))

		if self.payout_account_status in ("Ready", "Verified"):
			if not is_payout_admin():
				frappe.throw(_("Only an administrator can mark a payout account ready."))
			if not self.chapa_subaccount_id:
				frappe.throw(_("A Chapa subaccount ID is required before marking this account ready."))
			if self.has_value_changed("payout_account_status") or self.has_value_changed(
				"chapa_subaccount_id"
			):
				self.verified_on = now_datetime()
				self.verified_by = frappe.session.user
		elif self.has_value_changed("payout_account_status") and self.payout_account_status != "Disabled":
			self.verified_on = None
			self.verified_by = None


def is_payout_admin():
	return bool(ADMIN_ROLES & set(frappe.get_roles()))


def has_permission(doc, ptype="read", user=None):
	user = user or frappe.session.user
	roles = set(frappe.get_roles(user))
	if ADMIN_ROLES & roles:
		return True
	if "Course Creator" not in roles:
		return False
	if ptype == "create":
		return True
	return bool(doc and doc.teacher == user and ptype in ("read", "write", "select", "print"))


def get_permission_query_conditions(user=None):
	user = user or frappe.session.user
	roles = set(frappe.get_roles(user))
	if ADMIN_ROLES & roles:
		return ""
	if "Course Creator" not in roles:
		return "1 = 0"
	return f"`tabLMS Teacher Payout Account`.teacher = {frappe.db.escape(user)}"



@frappe.whitelist()
def get_chapa_banks():
    frappe.only_for(["System Manager", "Moderator", "Course Creator"])

    settings = get_chapa_settings()
    secret_key = settings.get_password("secret_key")

    if not secret_key:
        frappe.throw(_("Set a Chapa secret key before loading the bank list."))

    try:
        response = requests.get(
            BANKS_URL,
            headers={"Authorization": f"Bearer {secret_key}"},
            timeout=15,
        )
        response.raise_for_status()
        result = response.json()
    except (requests.RequestException, ValueError):
        frappe.throw(
            _("Unable to load Chapa's bank list. Check the Chapa settings and try again.")
        )

    if not isinstance(result, dict):
        frappe.throw(_("Chapa returned an unexpected bank-list response."))

    banks = result.get("data") or []

    if isinstance(banks, dict):
        banks = banks.get("data") or banks.get("banks") or []

    if not isinstance(banks, list) or not banks:
        frappe.throw(_("Chapa returned no banks. Please try again later."))

    return [
        {
            "code": str(code),
            "name": str(bank.get("name") or code),
        }
        for bank in banks
        if isinstance(bank, dict)
        for code in [
            bank.get("bank_code") or bank.get("id") or bank.get("code")
        ]
        if code
    ]



@frappe.whitelist()
def create_chapa_subaccount(name: str):
	frappe.only_for(["System Manager", "Moderator"])

	# Lock and mark the record before the external request. If the request times
	# out after Chapa creates the account, a later click must not create another.
	frappe.db.get_value("LMS Teacher Payout Account", name, "name", for_update=True)
	payout = frappe.get_doc("LMS Teacher Payout Account", name)
	if payout.chapa_subaccount_id:
		frappe.throw(_("This seller is already linked to a Chapa subaccount."))
	if payout.payout_account_status == "Disabled":
		frappe.throw(_("This payout account is disabled. Update its status before creating a subaccount."))
	if payout.payout_account_status == "Review Required":
		frappe.throw(
			_("A previous creation attempt needs reconciliation. Record the existing Chapa ID or resolve it before retrying.")
		)

	account_number = payout.get_password("account_number")
	if not all((payout.account_name, payout.business_name, payout.bank_code, account_number)):
		frappe.throw(_("Complete the seller's bank details before creating a Chapa subaccount."))
	if payout.split_type not in ("percentage", "flat") or payout.split_value is None:
		frappe.throw(_("Set the Chapa split type and value before creating a subaccount."))
	if payout.split_value <= 0 or (payout.split_type == "percentage" and payout.split_value > 1):
		frappe.throw(
			_("Split value must be positive; percentage splits must be entered as a decimal up to 1.0.")
		)

	settings = get_chapa_settings()
	secret_key = settings.get_password("secret_key")
	if not secret_key:
		frappe.throw(_("Set a Chapa secret key before creating subaccounts."))

	payout.payout_account_status = "Review Required"
	payout.setup_error = _("Subaccount creation is in progress; reconcile before retrying if the result is unknown.")
	payout.save(ignore_permissions=True)
	frappe.db.commit()

	payload = {
		"bank_code": payout.bank_code,
		"account_number": account_number,
		"business_name": payout.business_name,
		"account_name": payout.account_name,
		"split_type": payout.split_type,
		"split_value": payout.split_value,
	}

	try:
		response = requests.post(
			SUBACCOUNT_URL,
			json=payload,
			headers={"Authorization": f"Bearer {secret_key}", "Content-Type": "application/json"},
			timeout=30,
		)
	except requests.RequestException:
		# The request may have reached Chapa even if the response was lost. Leave
		# it in Review Required so an operator checks the dashboard before retrying.
		mark_creation_for_review(
			payout, _("Chapa's response was not received. Check the dashboard before retrying.")
		)
		return {"success": False, "message": _("Chapa's response was not received. Check the Chapa dashboard before retrying.")}

	try:
		result = response.json()
	except ValueError:
		result = None

	response_kind, subaccount_id = parse_subaccount_response(response.status_code, result)

	if response_kind == "created":
		payout.chapa_subaccount_id = subaccount_id
		payout.payout_account_status = "Pending Verification"
		payout.setup_error = None
		payout.save(ignore_permissions=True)
		return {"success": True, "subaccount_id": payout.chapa_subaccount_id}

	if response_kind == "duplicate":
		# Some Chapa errors may report a duplicate while returning its ID. Link
		# only that explicit ID; never infer it from bank details or an error text.
		payout.chapa_subaccount_id = subaccount_id
		payout.payout_account_status = "Pending Verification"
		payout.setup_error = None
		payout.save(ignore_permissions=True)
		return {"success": True, "subaccount_id": payout.chapa_subaccount_id, "existing": True}

	if response_kind == "duplicate_without_id":
		mark_creation_for_review(
			payout,
			_("Chapa reported an existing subaccount but did not return its ID. Reconcile it in Chapa and record the ID before retrying."),
		)
		return {"success": False, "message": payout.setup_error}

	if response_kind == "server_error":
		mark_creation_for_review(
			payout, _("Chapa returned a server error. Check the dashboard before retrying.")
		)
		return {"success": False, "message": _("Chapa returned a server error. Check its dashboard before retrying.")}
	if response_kind == "rejected":
		payout.payout_account_status = "Failed"
		payout.setup_error = _("Chapa rejected the bank details or split settings. Review them and try again.")
		payout.save(ignore_permissions=True)
		return {"success": False, "message": payout.setup_error}

	mark_creation_for_review(
		payout, _("Chapa did not confirm a subaccount ID. Check the dashboard before retrying.")
	)
	return {"success": False, "message": _("Chapa did not confirm a subaccount ID. Check its dashboard before retrying.")}


def parse_subaccount_response(status_code, result):
	"""Classify the V1 create response without guessing a subaccount ID."""
	if status_code >= 500:
		return "server_error", None

	if not isinstance(result, dict):
		return "uncertain", None

	data = result.get("data") or {}
	if isinstance(data, str):
		candidate_id = data
	elif isinstance(data, dict):
		candidate_id = data.get("subaccount_id") or data.get("id")
	else:
		candidate_id = None

	if status_code < 400 and result.get("status") == "success":
		return ("created", candidate_id) if is_valid_subaccount_id(candidate_id) else ("uncertain", None)

	if status_code >= 400:
		error = result.get("error")
		error_message = error.get("message") if isinstance(error, dict) else None
		message = " ".join(
			str(value)
			for value in (result.get("message"), error_message)
			if isinstance(value, str)
		).lower()
		if any(marker in message for marker in ("already exists", "already been created", "duplicate")):
			if is_valid_subaccount_id(candidate_id):
				return "duplicate", candidate_id
			return "duplicate_without_id", None
		return "rejected", None

	return "uncertain", None


def is_valid_subaccount_id(candidate_id):
	return isinstance(candidate_id, str) and bool(SUBACCOUNT_ID_PATTERN.fullmatch(candidate_id))


def mark_creation_for_review(payout, message):
	payout.payout_account_status = "Review Required"
	payout.setup_error = message
	payout.save(ignore_permissions=True)


@frappe.whitelist()
def mark_payout_account_ready(name: str):
	frappe.only_for(["System Manager", "Moderator"])
	payout = frappe.get_doc("LMS Teacher Payout Account", name)
	if not payout.chapa_subaccount_id:
		frappe.throw(_("Record or create a Chapa subaccount ID before marking this account ready."))
	if not all((payout.account_name, payout.business_name, payout.bank_code, payout.get_password("account_number"))):
		frappe.throw(_("Complete the seller's bank details before marking this account ready."))

	payout.payout_account_status = "Ready"
	payout.setup_error = None
	payout.save(ignore_permissions=True)
	return payout.payout_account_status


@frappe.whitelist()
def disable_payout_account(name: str):
	frappe.only_for(["System Manager", "Moderator"])
	payout = frappe.get_doc("LMS Teacher Payout Account", name)
	payout.payout_account_status = "Disabled"
	payout.save(ignore_permissions=True)
	return payout.payout_account_status


def get_chapa_settings():
	if not frappe.db.exists("Chapa Settings", "Chapa Settings"):
		frappe.throw(_("Configure Chapa Settings before managing seller payout accounts."))
	return frappe.get_doc("Chapa Settings", "Chapa Settings")
