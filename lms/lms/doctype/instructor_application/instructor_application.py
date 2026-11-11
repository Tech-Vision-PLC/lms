import re

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime

# The LMS decides "instructor" by Course Creator (see get_user_info, can_modify_course).
STUDENT_ROLE = "LMS Student"
INSTRUCTOR_ROLE = "Course Creator"
REVIEWER_ROLES = ("System Manager", "Moderator")

ACTIVE_STATUSES = ("Pending", "Under Review", "Approved", "Changes Requested")
REVIEW_STATUSES = ("Approved", "Rejected", "Changes Requested")

APPLICANT_FIELDS = (
	"full_name",
	"professional_title",
	"profile_image",
	"bio",
	"cv",
	"education",
	"experience",
	"expertise",
	"linkedin",
	"github",
	"portfolio",
	"teaching_reason",
	"proposed_course",
)
REQUIRED_FIELDS = {
	"full_name": "Full Name",
	"bio": "About You",
	"cv": "CV / Resume",
	"expertise": "Areas of Expertise",
	"teaching_reason": "Why Do You Want to Teach?",
	"proposed_course": "Course You Want to Teach",
}
URL_FIELDS = ("linkedin", "github", "portfolio")
FILE_FIELDS = ("cv", "profile_image")
MAX_TEXT_LENGTH = 5000

LMS_BASE = "/lms"

SERIALIZED_FIELDS = (
	"name",
	"status",
	"admin_notes",
	"creation",
	"modified",
	"reviewed_on",
	*APPLICANT_FIELDS,
)


class InstructorApplication(Document):
	def validate(self):
		self.validate_applicant()
		self.guard_status_change()

	def validate_applicant(self):
		if not self.applicant or not frappe.db.exists("User", self.applicant):
			frappe.throw(_("A valid applicant is required."))

		before = self.get_doc_before_save()
		if before and before.applicant != self.applicant:
			frappe.throw(_("The applicant cannot be changed."), frappe.PermissionError)

		if self.is_new() and frappe.db.exists(
			"Instructor Application",
			{
				"applicant": self.applicant,
				"status": ["in", ACTIVE_STATUSES],
				"name": ["!=", self.name],
			},
		):
			frappe.throw(_("This user already has an active instructor application."))

	def guard_status_change(self):
		"""Only reviewers may move an application between statuses. The applicant
		flow (flags.from_applicant, set only by the API below) may only produce Pending."""
		before = self.get_doc_before_save()

		if self.flags.from_applicant:
			if self.status != "Pending":
				frappe.throw(_("Invalid status."), frappe.PermissionError)
			return

		changed = (before.status != self.status) if before else (self.status != "Pending")
		if not changed:
			return

		if not _is_reviewer():
			frappe.throw(_("You are not allowed to change the application status."), frappe.PermissionError)

		if self.status in REVIEW_STATUSES:
			self.reviewed_by = frappe.session.user
			self.reviewed_on = now_datetime()

	def on_update(self):
		"""Role sync and applicant notification live here, not in the buttons, so
		changing the status from the Desk form behaves exactly like clicking Approve."""
		before = self.get_doc_before_save()
		previous = before.status if before else None

		if self.status == "Approved" and previous != "Approved":
			_grant_role(self.applicant, STUDENT_ROLE)  # keep/restore Student
			_grant_role(self.applicant, INSTRUCTOR_ROLE)
			frappe.clear_cache(user=self.applicant)
		elif previous == "Approved" and self.status != "Approved":
			# Approval withdrawn: drop only the instructor role; Student and others stay.
			frappe.db.delete("Has Role", {"parent": self.applicant, "parenttype": "User", "role": INSTRUCTOR_ROLE})
			frappe.clear_cache(user=self.applicant)

		if self.status in REVIEW_STATUSES and previous != self.status:
			self._notify_applicant()

	def _notify_applicant(self):
		messages = {
			"Approved": (
				_("Congratulations! Your instructor application has been approved. You can now create courses."),
				f"{LMS_BASE}/courses",
			),
			"Rejected": (
				_("Your instructor application was not approved. Open it to read the feedback."),
				f"{LMS_BASE}/become-an-instructor",
			),
			"Changes Requested": (
				_("Changes were requested on your instructor application. Please review the feedback and resubmit."),
				f"{LMS_BASE}/become-an-instructor",
			),
		}
		subject, link = messages[self.status]

		try:
			frappe.get_doc(
				{
					"doctype": "Notification Log",
					"for_user": self.applicant,
					"from_user": frappe.session.user,
					"type": "Alert",
					"subject": subject,
					"link": link,
					"document_type": "Instructor Application",
					"document_name": self.name,
				}
			).insert(ignore_permissions=True)
		except Exception:
			# A failed notification must never block the review or the role grant.
			frappe.log_error(title="Instructor Application notification failed")


# ---------------------------------------------------------------- helpers


def _is_reviewer() -> bool:
	return bool(set(REVIEWER_ROLES) & set(frappe.get_roles()))


def _require_user() -> str:
	if frappe.session.user == "Guest":
		frappe.throw(_("Please log in to continue."), frappe.PermissionError)
	return frappe.session.user


def _ensure_role(role: str):
	if not frappe.db.exists("Role", role):
		frappe.get_doc({"doctype": "Role", "role_name": role, "desk_access": 0}).insert(
			ignore_permissions=True
		)


def _grant_role(user: str, role: str):
	"""Additive only, never removes or replaces roles. Same pattern as api.save_role."""
	_ensure_role(role)
	if frappe.db.exists("Has Role", {"parent": user, "parenttype": "User", "role": role}):
		return
	doc = frappe.new_doc("Has Role")
	doc.parent = user
	doc.parenttype = "User"
	doc.parentfield = "roles"
	doc.role = role
	doc.insert(ignore_permissions=True)


def _lock_user(user: str):
	"""Serialise concurrent submissions by the same user (double click / scripted
	duplicates), since there is no DB unique constraint on applicant."""
	frappe.db.sql("select name from `tabUser` where name = %s for update", (user,))


def _get_latest(user: str):
	return frappe.db.get_value(
		"Instructor Application",
		{"applicant": user},
		list(SERIALIZED_FIELDS),
		order_by="creation desc",
		as_dict=True,
	)


def _check_file_ownership(file_url: str):
	"""Stops a user attaching someone else's private file as their CV."""
	if file_url and not frappe.db.exists("File", {"file_url": file_url, "owner": frappe.session.user}):
		frappe.throw(_("Invalid file. Please upload the file again."), frappe.PermissionError)


def _clean_payload(data) -> dict:
	if isinstance(data, str):
		data = frappe.parse_json(data)
	if not isinstance(data, dict):
		frappe.throw(_("Invalid application data."))

	# Whitelist: applicant, status, reviewed_*, admin_notes are never read from the client.
	payload = {}
	for field in APPLICANT_FIELDS:
		value = data.get(field)
		if value is None:
			payload[field] = None
			continue
		if not isinstance(value, str):
			frappe.throw(_("Invalid value for {0}.").format(field))
		value = value.strip()
		if field not in FILE_FIELDS and field not in URL_FIELDS and len(value) > MAX_TEXT_LENGTH:
			frappe.throw(_("{0} is too long.").format(REQUIRED_FIELDS.get(field, field)))
		payload[field] = value or None

	missing = [label for field, label in REQUIRED_FIELDS.items() if not payload.get(field)]
	if missing:
		frappe.throw(_("Please fill in: {0}").format(", ".join(missing)))

	for field in URL_FIELDS:
		value = payload.get(field)
		if not value:
			continue
		# Reject javascript:, data:, etc. Bare "linkedin.com/in/x" gets https://.
		if re.match(r"^(?!https?://)[a-z][a-z0-9+.\-]*:", value, re.I):
			frappe.throw(_("Please enter a valid link for {0}.").format(field.title()))
		if not re.match(r"^https?://", value, re.I):
			payload[field] = "https://" + value

	for field in FILE_FIELDS:
		_check_file_ownership(payload.get(field))

	return payload


def _attach_files(doc):
	"""Link the uploaded files to the application so reviewers can open the private CV."""
	for field in FILE_FIELDS:
		url = doc.get(field)
		if not url:
			continue
		for name in frappe.get_all(
			"File",
			{"file_url": url, "owner": doc.applicant, "attached_to_doctype": ["is", "not set"]},
			pluck="name",
		):
			frappe.db.set_value(
				"File",
				name,
				{
					"attached_to_doctype": "Instructor Application",
					"attached_to_name": doc.name,
					"attached_to_field": field,
				},
				update_modified=False,
			)


def _serialize(doc) -> dict:
	return {field: doc.get(field) for field in SERIALIZED_FIELDS}


# ------------------------------------------------------- applicant endpoints


@frappe.whitelist()
def get_my_application():
	"""The caller's latest application, or None. Filtered by session user, so no
	client-supplied id exists to tamper with."""
	user = _require_user()
	return _get_latest(user)


@frappe.whitelist()
def submit_application(data: str | dict):
	user = _require_user()
	payload = _clean_payload(data)

	if INSTRUCTOR_ROLE in frappe.get_roles(user):
		frappe.throw(_("You already have instructor access."))

	_lock_user(user)
	latest = _get_latest(user)
	# A Rejected applicant may apply again; every other state blocks a new record.
	if latest and latest.status != "Rejected":
		frappe.throw(_("You already have an instructor application."))

	doc = frappe.new_doc("Instructor Application")
	doc.update(payload)
	doc.applicant = user  # always the authenticated user
	doc.status = "Pending"
	doc.flags.from_applicant = True
	doc.insert(ignore_permissions=True)
	_attach_files(doc)
	return _serialize(doc)


@frappe.whitelist()
def resubmit_application(data: str | dict):
	user = _require_user()
	payload = _clean_payload(data)

	_lock_user(user)
	latest = _get_latest(user)
	if not latest or latest.status != "Changes Requested":
		frappe.throw(_("There is no application awaiting changes."))

	doc = frappe.get_doc("Instructor Application", latest.name)
	doc.update(payload)
	doc.status = "Pending"
	doc.admin_notes = None
	doc.reviewed_by = None
	doc.reviewed_on = None
	doc.flags.from_applicant = True
	doc.save(ignore_permissions=True)
	_attach_files(doc)
	return _serialize(doc)


# ---------------------------------------------------------- admin endpoints


def _review(name: str, status: str, admin_notes: str | None):
	_require_user()
	frappe.only_for(REVIEWER_ROLES)  # server-side gate; Administrator passes

	if not isinstance(name, str) or not frappe.db.exists("Instructor Application", name):
		frappe.throw(_("Application not found."), frappe.DoesNotExistError)

	admin_notes = (admin_notes or "").strip()
	if status in ("Rejected", "Changes Requested") and not admin_notes:
		frappe.throw(_("Please add notes explaining your decision."))

	doc = frappe.get_doc("Instructor Application", name)
	if admin_notes:
		doc.admin_notes = admin_notes
	doc.status = status
	doc.save(ignore_permissions=True)  # reviewer already verified; validate() stamps reviewed_by/on
	return doc.status


@frappe.whitelist()
def approve_application(name: str, admin_notes: str | None = None):
	return _review(name, "Approved", admin_notes)


@frappe.whitelist()
def reject_application(name: str, admin_notes: str | None = None):
	return _review(name, "Rejected", admin_notes)


@frappe.whitelist()
def request_changes(name: str, admin_notes: str | None = None):
	return _review(name, "Changes Requested", admin_notes)