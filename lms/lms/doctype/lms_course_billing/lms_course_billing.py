# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


SNAPSHOT_FIELDS = (
	"payment_reference",
	"course",
	"batch",
	"teacher",
	"student",
	"course_amount",
	"discount_amount",
	"tax_amount",
	"gross_amount",
	"currency",
	"commission_rate",
	"commission_amount",
	"expected_teacher_amount",
	"chapa_tx_ref",
)


class LMSCourseBilling(Document):
	def validate(self):
		self.validate_snapshot()
		self.validate_amounts()

	def validate_snapshot(self):
		if not self.course and not self.batch:
			frappe.throw(_("Select the course or batch covered by this billing record."))

		if not self.is_new() and any(self.has_value_changed(field) for field in SNAPSHOT_FIELDS):
			frappe.throw(
				_("Billing snapshot fields cannot be changed after creation. Create an adjustment record instead.")
			)

	def validate_amounts(self):
		for field in (
			"course_amount",
			"discount_amount",
			"tax_amount",
			"gross_amount",
			"commission_amount",
			"expected_teacher_amount",
			"gateway_fee",
			"reported_teacher_amount",
		):
			if self.get(field) is not None and self.get(field) < 0:
				frappe.throw(_("{0} cannot be negative.").format(self.meta.get_label(field)))

		if self.commission_rate is not None and not 0 <= self.commission_rate <= 100:
			frappe.throw(_("Commission rate must be between 0 and 100."))
