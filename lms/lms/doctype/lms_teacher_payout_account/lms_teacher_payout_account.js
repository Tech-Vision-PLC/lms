frappe.ui.form.on("LMS Teacher Payout Account", {
	onload(frm) {
		if (frm.is_new() && frappe.user.has_role("Course Creator")) {
			frm.set_value("teacher", frappe.session.user);
		}

		frappe.call({
			method: "lms.lms.doctype.lms_teacher_payout_account.lms_teacher_payout_account.get_chapa_banks",
		}).then((response) => {
			const banks = response.message || [];
			const codes = banks.map((bank) => bank.code);
			if (frm.doc.bank_code && !codes.includes(frm.doc.bank_code)) {
				codes.push(frm.doc.bank_code);
			}
			frm.set_df_property("bank_code", "options", ["", ...codes].join("\n"));
			frm._chapa_banks = Object.fromEntries(banks.map((bank) => [bank.code, bank.name]));
			frm.set_value("bank_name", frm._chapa_banks[frm.doc.bank_code] || frm.doc.bank_name);
		});
	},

	refresh(frm) {
		if (frm.is_new() || !has_payout_admin_role()) return;

		if (
			!frm.doc.chapa_subaccount_id &&
			frm.doc.payout_account_status !== "Review Required" &&
			frm.doc.payout_account_status !== "Disabled"
		) {
			frm.add_custom_button(__("Create Chapa Subaccount"), () => {
				frappe.call({
					method: "lms.lms.doctype.lms_teacher_payout_account.lms_teacher_payout_account.create_chapa_subaccount",
					args: { name: frm.doc.name },
					freeze: true,
					freeze_message: __("Creating Chapa subaccount..."),
				}).then((response) => {
					const result = response.message || {};
					if (result.success) {
						frappe.show_alert({ message: __("Subaccount created. Review and mark the payout account ready."), indicator: "green" });
						frm.reload_doc();
					} else if (result.message) {
						frappe.msgprint(result.message);
						frm.reload_doc();
					}
				});
			});
		}

		if (frm.doc.chapa_subaccount_id && frm.doc.payout_account_status !== "Ready") {
			frm.add_custom_button(__("Mark Payout Account Ready"), () => {
				frappe.call({
					method: "lms.lms.doctype.lms_teacher_payout_account.lms_teacher_payout_account.mark_payout_account_ready",
					args: { name: frm.doc.name },
					freeze: true,
				}).then(() => frm.reload_doc());
			});
		}

		if (frm.doc.payout_account_status !== "Disabled") {
			frm.add_custom_button(__("Disable Payout Account"), () => {
				frappe.call({
					method: "lms.lms.doctype.lms_teacher_payout_account.lms_teacher_payout_account.disable_payout_account",
					args: { name: frm.doc.name },
					freeze: true,
				}).then(() => frm.reload_doc());
			});
		}
	},

	bank_code(frm) {
		frm.set_value("bank_name", frm._chapa_banks?.[frm.doc.bank_code] || "");
	},
});

function has_payout_admin_role() {
	return frappe.user.has_role("System Manager") || frappe.user.has_role("Moderator");
}
