import secrets
import string

import frappe


def create_referral_code(doc, method=None):
    """Create one unique referral code for each newly created user."""

    if frappe.db.exists("Referral Code", {"user": doc.name}):
        return

    alphabet = string.ascii_uppercase + string.digits

    while True:
        code = "REF-" + "".join(
            secrets.choice(alphabet) for _ in range(8)
        )

        if not frappe.db.exists(
            "Referral Code",
            {"referral_code": code},
        ):
            break

    frappe.get_doc({
        "doctype": "Referral Code",
        "user": doc.name,
        "referral_code": code,
    }).insert(ignore_permissions=True)

    frappe.logger("referral").info(
        f"Created referral code for user {doc.name}"
    )


def award_referral_points(referral):
    """Award 10 points to the referrer for a successful referral."""

    if frappe.db.exists(
        "Referral Point",
        {"referral": referral.name},
    ):
        return

    frappe.get_doc({
        "doctype": "Referral Point",
        "user": referral.referrer,
        "points": 10,
        "referral": referral.name,
        "status": "awarded",
        "awarded_on": frappe.utils.now_datetime(),
        "reason": "Successful referral signup",
    }).insert(ignore_permissions=True)

    frappe.logger("referral").info(
        f"Awarded 10 referral points to {referral.referrer} "
        f"for referral {referral.name}"
    )


@frappe.whitelist()
def get_my_referral_data():
    """Return the current user's referral code and referral statistics."""
    user = frappe.session.user

    if user == "Guest":
        frappe.throw("Please log in to view your referral information.")

    code = frappe.db.get_value(
        "Referral Code",
        {"user": user},
        "referral_code",
    )

    # Handle existing users whose referral code was not created.
    if not code:
        create_referral_code(frappe.get_doc("User", user))
        code = frappe.db.get_value(
            "Referral Code",
            {"user": user},
            "referral_code",
        )

    successful_referrals = frappe.db.count(
        "Referral",
        {"referrer": user},
    )

    return {
        "referral_code": code,
        "referral_count": successful_referrals,
        "referral_link": (
            f"{frappe.utils.get_url()}/lms/referrals?code={code}"
            if code
            else None
        ),
    }


@frappe.whitelist()
def apply_referral_code(code: str):
    """Apply a referral code for the logged-in user."""
    referred_user = frappe.session.user

    if referred_user == "Guest":
        frappe.throw("Please log in before applying a referral code.")

    code = (code or "").strip().upper()

    if not code:
        frappe.throw("Please enter a referral code.")

    referral_code_doc = frappe.db.get_value(
        "Referral Code",
        {"referral_code": code},
        ["name", "user"],
        as_dict=True,
    )

    if not referral_code_doc:
        frappe.throw("This referral code is invalid.")

    referrer = referral_code_doc.user

    if referrer == referred_user:
        frappe.throw("You cannot apply your own referral code.")

    if frappe.db.exists("Referral", {"referred_user": referred_user}):
        frappe.throw("You have already applied a referral code.")

    referral = frappe.get_doc({
        "doctype": "Referral",
        "referrer": referrer,
        "referred_user": referred_user,
        "referral_code": referral_code_doc.name,
    })
    referral.insert(ignore_permissions=True)

    award_referral_points(referral)

    return {"success": True, "message": "Referral code applied successfully."}


def attribute_new_user_from_referral(doc, method=None):
    """Attribute a newly created website user using a captured referral cookie.

    Referral failures must never prevent user registration.
    """
    if getattr(doc, "user_type", None) != "Website User":
        return

    request = getattr(frappe.local, "request", None)
    if request is None:
        return

    code = (request.cookies.get("lms_referral_code") or "").strip().upper()
    if not code:
        return

    try:
        referral_code_doc = frappe.db.get_value(
            "Referral Code",
            {"referral_code": code},
            ["name", "user"],
            as_dict=True,
        )

        if not referral_code_doc:
            frappe.logger("referral").warning(
                f"Invalid referral code received during signup: {code}"
            )
            return

        referrer = referral_code_doc.user

        if not referrer or referrer == doc.name:
            return

        if frappe.db.exists("Referral", {"referred_user": doc.name}):
            return

        referral = frappe.get_doc({
            "doctype": "Referral",
            "referrer": referrer,
            "referred_user": doc.name,
            "referral_code": referral_code_doc.name,
        })
        referral.insert(ignore_permissions=True)

        award_referral_points(referral)

        frappe.logger("referral").info(
            f"Attributed new user {doc.name} to referrer {referrer}"
        )

    except Exception:
        frappe.log_error(
            title="Referral attribution failed",
            message=frappe.get_traceback(),
        )

    finally:
        try:
            cookie_manager = getattr(frappe.local, "cookie_manager", None)
            if cookie_manager:
                cookie_manager.delete_cookie("lms_referral_code")
        except Exception:
            frappe.logger("referral").warning(
                "Could not clear the referral attribution cookie."
            )
