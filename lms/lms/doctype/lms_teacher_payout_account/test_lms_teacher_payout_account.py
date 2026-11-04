# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

from frappe.tests import UnitTestCase

from lms.lms.doctype.lms_teacher_payout_account.lms_teacher_payout_account import (
	is_valid_subaccount_id,
	parse_subaccount_response,
)


class TestLMSTeacherPayoutAccount(UnitTestCase):
	def test_create_response_with_id_is_accepted(self):
		kind, subaccount_id = parse_subaccount_response(
			200, {"status": "success", "data": {"subaccount_id": "sub_abc123"}}
		)

		self.assertEqual((kind, subaccount_id), ("created", "sub_abc123"))

	def test_explicit_duplicate_response_links_returned_id(self):
		kind, subaccount_id = parse_subaccount_response(
			409,
			{
				"status": "error",
				"message": "Subaccount already exists",
				"data": {"subaccount_id": "sub_existing123"},
			},
		)

		self.assertEqual((kind, subaccount_id), ("duplicate", "sub_existing123"))

	def test_duplicate_without_id_requires_reconciliation(self):
		kind, subaccount_id = parse_subaccount_response(
			409, {"status": "error", "message": "Subaccount already exists"}
		)

		self.assertEqual((kind, subaccount_id), ("duplicate_without_id", None))

	def test_ambiguous_error_id_is_not_linked(self):
		kind, subaccount_id = parse_subaccount_response(
			409,
			{
				"status": "error",
				"message": "Duplicate request; matching subaccounts were found",
				"data": {"subaccount_id": ["sub_one", "sub_two"]},
			},
		)

		self.assertEqual((kind, subaccount_id), ("duplicate_without_id", None))

	def test_success_response_without_valid_id_is_uncertain(self):
		for payload in (
			{"status": "success", "data": {}},
			{"status": "success", "data": {"subaccount_id": ""}},
			{"status": "success", "data": {"subaccount_id": "invalid id"}},
		):
			with self.subTest(payload=payload):
				self.assertEqual(parse_subaccount_response(200, payload), ("uncertain", None))

	def test_api_failures_are_classified_safely(self):
		self.assertEqual(parse_subaccount_response(502, {"status": "error"}), ("server_error", None))
		self.assertEqual(parse_subaccount_response(400, {"status": "error"}), ("rejected", None))
		self.assertEqual(parse_subaccount_response(200, None), ("uncertain", None))

	def test_subaccount_id_validation(self):
		self.assertTrue(is_valid_subaccount_id("sub_abc-123"))
		self.assertFalse(is_valid_subaccount_id("account number 123"))
		self.assertFalse(is_valid_subaccount_id(123))
