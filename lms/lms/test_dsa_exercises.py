import json
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock, patch

import frappe

from lms.lms.api import get_assessment_from_lesson, get_course_programming_exercise_progress
from lms.lms.doctype.course_lesson.course_lesson import CourseLesson


def lesson_content():
	return json.dumps(
		{
			"blocks": [
				{"type": "program", "data": {"exercise": "exercise-1"}},
				{"type": "program", "data": {"dsa_problem": "problem-1"}},
				{"type": "program", "data": {}},
			]
		}
	)


class TestDSAExercises(TestCase):
	@patch("lms.lms.api.frappe.get_all")
	def test_existing_and_dsa_references_are_separate(self, get_all):
		get_all.return_value = [frappe._dict(content=lesson_content())]
		self.assertEqual(get_assessment_from_lesson("course-1", "program"), ["exercise-1"])
		self.assertEqual(get_assessment_from_lesson("course-1", "program", "dsa_problem"), ["problem-1"])

	@patch("lms.lms.api.frappe.get_installed_apps", return_value=["lms", "dsa"])
	@patch("lms.lms.api.frappe.db", new_callable=MagicMock)
	@patch("lms.lms.api.frappe.get_all")
	def test_progress_uses_the_students_latest_dsa_submission(self, get_all, db, apps):
		get_all.side_effect = [
			[frappe._dict(content=lesson_content())],
			[frappe._dict(exercise="exercise-1", status="Passed")],
			[frappe._dict(content=lesson_content())],
			[frappe._dict(status="Accepted")],
		]
		db.get_value.return_value = "Two Sum"
		result = get_course_programming_exercise_progress("course-1", "student@example.com")
		self.assertEqual(
			result[1], {"exercise": "problem-1", "exercise_title": "Two Sum", "status": "Accepted"}
		)
		self.assertEqual(
			get_all.call_args.kwargs["filters"], {"problem": "problem-1", "member": "student@example.com"}
		)
		self.assertEqual(get_all.call_args.kwargs["limit"], 1)

	@patch("lms.lms.api.frappe.get_installed_apps", return_value=["lms"])
	@patch("lms.lms.api.frappe.get_all", return_value=[])
	def test_lms_without_dsa_does_not_query_dsa_tables(self, get_all, apps):
		self.assertEqual(get_course_programming_exercise_progress("course-1", "student@example.com"), [])
		get_all.assert_called_once()

	@patch(
		"lms.lms.doctype.course_lesson.course_lesson.frappe.get_installed_apps", return_value=["lms", "dsa"]
	)
	@patch("lms.lms.doctype.course_lesson.course_lesson.frappe.db", new_callable=MagicMock)
	def test_lesson_keeps_existing_problem_reference(self, db, apps):
		db.exists.return_value = True
		lesson = SimpleNamespace(content=lesson_content(), instructor_content=None)
		CourseLesson.validate_dsa_problems(lesson)
		db.exists.assert_called_once_with("DSAProblem", "problem-1")

	@patch("lms.lms.doctype.course_lesson.course_lesson._", side_effect=lambda text: text)
	@patch("lms.lms.doctype.course_lesson.course_lesson.frappe.throw", side_effect=frappe.ValidationError)
	@patch(
		"lms.lms.doctype.course_lesson.course_lesson.frappe.get_installed_apps", return_value=["lms", "dsa"]
	)
	@patch("lms.lms.doctype.course_lesson.course_lesson.frappe.db", new_callable=MagicMock)
	def test_missing_problem_is_rejected_before_saving(self, db, apps, throw, translate):
		db.exists.return_value = False
		lesson = SimpleNamespace(content=lesson_content(), instructor_content=None)
		with self.assertRaises(frappe.ValidationError):
			CourseLesson.validate_dsa_problems(lesson)
