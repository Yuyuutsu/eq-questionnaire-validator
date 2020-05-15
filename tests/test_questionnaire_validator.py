import os
from json import load

from structlog import configure
from structlog import getLogger
from structlog.stdlib import LoggerFactory

from app import error_messages
from app.validators.questionnaire_validator import QuestionnaireValidator
from app.validators.schema_validator import SchemaValidator

logger = getLogger()

configure(logger_factory=LoggerFactory())


def _open_and_load_schema_file(file):
    json_file = open(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), file), encoding="utf8"
    )
    json_to_validate = load(json_file)

    return json_to_validate


def test_param_valid_schemas(valid_schema_filename):
    """
    Uses py.test generated tests to validate all schemas contained in the 'valid' folder.
    """
    with open(valid_schema_filename, encoding="utf8") as json_file:
        json_to_validate = load(json_file)

        validator = QuestionnaireValidator(json_to_validate)
        schema_validator = SchemaValidator(json_to_validate)

        schema_validator.validate()
        validator.validate()

        assert not validator.errors
        assert not schema_validator.errors


def test_answer_comparisons_different_types():
    """ Ensures that when answer comparison is used, the type of the variables must be the same """
    filename = "schemas/invalid/test_invalid_answer_comparison_types.json"

    validator = QuestionnaireValidator(_open_and_load_schema_file(filename))
    validator.validate()

    expected_errors = [
        {
            "message": error_messages.NON_MATCHING_WHEN_ANSWER_AND_COMPARISON_TYPES,
            "comparison_id": "route-comparison-1-answer",
            "answer_id": "route-comparison-2-answer",
            "referenced_id": "route-comparison-2",
        },
        {
            "message": error_messages.NON_CHECKBOX_COMPARISON_ID,
            "comparison_id": "route-comparison-2-answer",
            "condition": "equals any",
        },
        {
            "message": error_messages.NON_MATCHING_WHEN_ANSWER_AND_COMPARISON_TYPES,
            "comparison_id": "comparison-2-answer",
            "answer_id": "comparison-1-answer",
            "referenced_id": "equals-answers",
        },
        {
            "message": error_messages.NON_MATCHING_WHEN_ANSWER_AND_COMPARISON_TYPES,
            "comparison_id": "comparison-2-answer",
            "answer_id": "comparison-1-answer",
            "referenced_id": "less-than-answers",
        },
        {
            "message": error_messages.NON_MATCHING_WHEN_ANSWER_AND_COMPARISON_TYPES,
            "comparison_id": "comparison-2-answer",
            "answer_id": "comparison-1-answer",
            "referenced_id": "less-than-answers",
        },
    ]

    assert expected_errors == validator.errors


def test_answer_comparisons_invalid_comparison_id():
    """ Ensures that when answer comparison is used, the comparison_id is a valid answer id"""
    filename = "schemas/invalid/test_invalid_answer_comparison_id.json"

    expected_error_messages = [
        {
            "message": error_messages.NON_EXISTENT_WHEN_KEY,
            "answer_id": "bad-answer-id-2",
            "key": "comparison.id",
            "referenced_id": "route-comparison-2",
        },
        {
            "message": error_messages.NON_EXISTENT_WHEN_KEY,
            "answer_id": "bad-answer-id-3",
            "key": "comparison.id",
            "referenced_id": "equals-answers",
        },
        {
            "message": error_messages.NON_EXISTENT_WHEN_KEY,
            "answer_id": "bad-answer-id-4",
            "key": "comparison.id",
            "referenced_id": "less-than-answers",
        },
        {
            "message": error_messages.NON_EXISTENT_WHEN_KEY,
            "answer_id": "bad-answer-id-5",
            "key": "comparison.id",
            "referenced_id": "less-than-answers",
        },
        {
            "message": error_messages.NON_EXISTENT_WHEN_KEY,
            "answer_id": "bad-answer-id-6",
            "key": "comparison.id",
            "referenced_id": "greater-than-answers",
        },
        {
            "message": error_messages.NON_EXISTENT_WHEN_KEY,
            "answer_id": "bad-answer-id-7",
            "key": "id",
            "referenced_id": "greater-than-answers",
        },
    ]

    json_to_validate = _open_and_load_schema_file(filename)
    questionnaire_validator = QuestionnaireValidator(json_to_validate)
    questionnaire_validator.validate()

    assert expected_error_messages == questionnaire_validator.errors


def test_invalid_mutually_exclusive_conditions():
    filename = "schemas/invalid/test_invalid_mutually_exclusive_conditions.json"

    validator = QuestionnaireValidator(_open_and_load_schema_file(filename))
    validator.validate()

    expected_errors = [
        {
            "message": error_messages.MUTUALLY_EXCLUSIVE_CONTAINS_MANDATORY,
            "question_id": "mutually-exclusive-date-question",
        },
        {
            "message": error_messages.NON_CHECKBOX_ANSWER,
            "answer_id": "mutually-exclusive-date-answer-2",
            "question_id": "mutually-exclusive-date-question",
        },
    ]

    assert expected_errors == validator.errors


def test_invalid_string_transforms():
    filename = "schemas/invalid/test_invalid_string_transforms.json"

    validator = QuestionnaireValidator(_open_and_load_schema_file(filename))
    validator.validate()

    expected_errors = [
        {
            "message": error_messages.PLACEHOLDERS_DONT_MATCH_DEFINITIONS,
            "text": "test {answer1}",
            "differences": {"answer1"},
        },
        {
            "message": error_messages.PLACEHOLDERS_DONT_MATCH_DEFINITIONS,
            "text": "test {answer1} and {answer2}",
            "differences": {"answer2"},
        },
        {
            "message": error_messages.FIRST_TRANSFORM_CONTAINS_PREVIOUS_TRANSFORM_REF,
            "block_id": "block4",
        },
        {
            "message": error_messages.NO_PREVIOUS_TRANSFORM_REF_IN_CHAIN,
            "block_id": "block5",
        },
    ]

    assert expected_errors == validator.errors


def test_invalid_placeholder_answer_ids():
    filename = "schemas/invalid/test_invalid_placeholder_source_ids.json"

    validator = QuestionnaireValidator(_open_and_load_schema_file(filename))
    validator.validate()

    expected_errors = [
        {
            "message": error_messages.ANSWER_REFERENCE_INVALID,
            "block_id": "block1",
            "referenced_id": "invalid-answer0",
        },
        {
            "message": error_messages.ANSWER_REFERENCE_INVALID,
            "block_id": "block2",
            "referenced_id": "invalid-answer1",
        },
        {
            "message": error_messages.ANSWER_SELF_REFERENCE,
            "block_id": "block3",
            "referenced_id": "answer4",
        },
        {
            "message": error_messages.METADATA_REFERENCE_INVALID,
            "block_id": "block4",
            "referenced_id": "invalid-metadata-ref",
        },
    ]

    assert validator.errors == expected_errors


def test_invalid_placeholder_list_reference():
    filename = "schemas/invalid/test_invalid_placeholder_plurals.json"

    validator = QuestionnaireValidator(_open_and_load_schema_file(filename))
    validator.validate()

    expected_errors = [
        {
            "message": error_messages.LIST_REFERENCE_INVALID,
            "block_id": "block1",
            "id": "people",
        },
        {
            "message": error_messages.LIST_REFERENCE_INVALID,
            "block_id": "block1",
            "id": "people",
        },
    ]

    assert expected_errors == validator.errors


def test_single_variant_invalid():
    file_name = "schemas/invalid/test_invalid_single_variant.json"

    validator = QuestionnaireValidator(_open_and_load_schema_file(file_name))
    validator.validate()

    assert {
        "message": error_messages.VARIANTS_HAS_ONE_VARIANT,
        "block_id": "block-2"
    } in validator.errors


def test_duplicate_answer_ids():
    filename = "schemas/invalid/test_invalid_duplicate_ids.json"

    validator = QuestionnaireValidator(_open_and_load_schema_file(filename))
    validator.validate_duplicates()

    expected_errors = [
        {"message": error_messages.DUPLICATE_ID_FOUND, "id": "block-1"},
        {"message": error_messages.DUPLICATE_ID_FOUND, "id": "answer-2"},
        {"message": error_messages.DUPLICATE_ID_FOUND, "id": "question-1"},
        {"message": error_messages.DUPLICATE_ID_FOUND, "id": "block-2"},
    ]

    assert all(
        [expected_error in validator.errors for expected_error in expected_errors]
    )


def test_invalid_list_collector_non_radio():
    filename = "schemas/invalid/test_invalid_list_collector_non_radio.json"

    validator = QuestionnaireValidator(_open_and_load_schema_file(filename))
    validator.validate()

    expected_error_messages = [
        {
            "message": error_messages.NO_RADIO_FOR_LIST_COLLECTOR,
            "block_id": "list-collector",
        }
    ]

    assert expected_error_messages == validator.errors


def test_primary_person_invalid_list_collector_non_radio():
    filename = (
        "schemas/invalid/test_invalid_primary_person_list_collector_no_radio.json"
    )

    validator = QuestionnaireValidator(_open_and_load_schema_file(filename))
    validator.validate()

    expected_errors = [
        {
            "message": error_messages.NO_RADIO_FOR_PRIMARY_PERSON_LIST_COLLECTOR,
            "block_id": "primary-person-list-collector",
        }
    ]

    assert expected_errors == validator.errors


def test_invalid_list_collector_with_no_add_option():
    filename = "schemas/invalid/test_invalid_list_collector_with_no_add_option.json"

    validator = QuestionnaireValidator(_open_and_load_schema_file(filename))
    validator.validate()

    expected_errors = [
        {
            "message": error_messages.NON_EXISTENT_LIST_COLLECTOR_ADD_ANSWER_VALUE,
            "block_id": "list-collector",
        }
    ]

    assert expected_errors == validator.errors


def test_invalid_primary_person_list_collector_with_no_add_option():
    filename = "schemas/invalid/test_invalid_primary_person_list_collector_bad_answer_value.json"

    validator = QuestionnaireValidator(_open_and_load_schema_file(filename))
    validator.validate()

    expected_errors = [
        {
            "message": error_messages.NON_EXISTENT_PRIMARY_PERSON_LIST_COLLECTOR_ANSWER_VALUE,
            "block_id": "primary-person-list-collector",
        }
    ]

    assert expected_errors == validator.errors


def test_invalid_list_reference_in_custom_summary():
    filename = "schemas/invalid/test_invalid_custom_list_summary.json"

    validator = QuestionnaireValidator(_open_and_load_schema_file(filename))

    expected_errors = [
        {"message": error_messages.FOR_LIST_NEVER_POPULATED, "list_name": "household"}
    ]

    validator.validate()

    assert validator.errors == expected_errors


def test_inconsistent_ids_in_variants():
    file_name = "schemas/invalid/test_invalid_inconsistent_ids_in_variants.json"
    json_to_validate = _open_and_load_schema_file(file_name)

    validator = QuestionnaireValidator(json_to_validate)
    validator.validate()

    assert [
        {
            "message": error_messages.VARIANTS_HAVE_DIFFERENT_ANSWER_LIST_LENGTHS,
            "block_id": "block-2",
        },
        {
            "message": error_messages.VARIANTS_HAVE_DIFFERENT_QUESTION_IDS,
            "block_id": "block-2",
            "question_ids": {"question-2", "question-2-variant"},
        },
        {
            "message": error_messages.VARIANTS_HAVE_MISMATCHED_ANSWER_IDS,
            "block_id": "block-2",
            "answer_ids": {'answer-2', 'answer-2-variant', 'answer-3'}
        },
    ] == validator.errors

    assert len(validator.errors) == 3


def test_inconsistent_default_answers_in_variants():
    file_name = (
        "schemas/invalid/test_invalid_inconsistent_default_answers_in_variants.json"
    )
    json_to_validate = _open_and_load_schema_file(file_name)

    validator = QuestionnaireValidator(json_to_validate)
    validator.validate()

    assert [{
        'message': error_messages.VARIANTS_HAVE_DIFFERENT_DEFAULT_ANSWERS,
        'block_id': 'block-2',
        'question_ids': {'question-2'}
    }] == validator.errors


def test_invalid_list_collector_duplicate_ids_between_list_collectors():
    filename = "schemas/invalid/test_invalid_list_collector_duplicate_ids_multiple_collectors.json"

    validator = QuestionnaireValidator(_open_and_load_schema_file(filename))
    validator.validate()

    expected_errors = [
        {"message": error_messages.DUPLICATE_ID_FOUND, "id": "add-person"},
        {"message": error_messages.DUPLICATE_ID_FOUND, "id": "remove-person"},
        {"message": error_messages.DUPLICATE_ID_FOUND, "id": "edit-person"},
    ]

    assert all(
        [expected_error in validator.errors for expected_error in expected_errors]
    )


def test_inconsistent_types_in_variants():
    file_name = "schemas/invalid/test_invalid_inconsistent_types_in_variants.json"
    json_to_validate = _open_and_load_schema_file(file_name)

    validator = QuestionnaireValidator(json_to_validate)
    validator.validate()

    expected_errors = [
        {
            "message": error_messages.VARIANTS_HAVE_MULTIPLE_QUESTION_TYPES,
            'block_id': 'block-2',
            'question_types': {'NotGeneral', 'General'}
        },
        {
            "message": error_messages.VARIANTS_HAVE_MISMATCHED_ANSWER_TYPES,
            'block_id': 'block-2',
            'answer_id': 'answer-2',
            'answer_types': {'NotANumber', 'Number'}
        }
    ]

    assert expected_errors == validator.errors


def test_invalid_when_condition_property():
    filename = "schemas/invalid/test_invalid_when_condition_property.json"

    validator = QuestionnaireValidator(_open_and_load_schema_file(filename))

    expected_errors = [
        {
            "message": error_messages.NON_CHECKBOX_COMPARISON_ID,
            "comparison_id": "country-checkbox-answer2",
            "condition": "contains any",
        },
        {
            "message": error_messages.CHECKBOX_MUST_USE_CORRECT_CONDITION,
            "condition": "equals any",
            "answer_id": "country-checkbox-answer",
        },
    ]

    validator.validate()

    assert validator.errors == expected_errors


def test_invalid_list_name_in_when_rule():
    filename = "schemas/invalid/test_invalid_when_condition_list_property.json"
    validator = QuestionnaireValidator(_open_and_load_schema_file(filename))

    expected_errors = [
        {
            "message": error_messages.LIST_REFERENCE_INVALID,
            "list_name": "non-existent-list-name",
        }
    ]

    validator.validate()

    assert validator.errors == expected_errors


def test_invalid_relationship_no_list_specified():
    filename = "schemas/invalid/test_invalid_relationship_list_doesnt_exist.json"

    validator = QuestionnaireValidator(_open_and_load_schema_file(filename))
    validator.validate()

    expected_for_list_error = [
        {
            "message": error_messages.FOR_LIST_NEVER_POPULATED,
            "list_name": "not-a-list",
            "block_id": "relationships",
        }
    ]

    expected_answer_errors = [
        {
            "message": error_messages.ANSWER_REFERENCE_INVALID,
            "referenced_id": "first-name",
            "block_id": "relationships",
        },
        {
            "message": error_messages.ANSWER_REFERENCE_INVALID,
            "referenced_id": "last-name",
            "block_id": "relationships",
        },
    ] * 12

    assert validator.errors == expected_answer_errors + expected_for_list_error


def test_invalid_hub_and_spoke_with_summary_confirmation():
    filename = (
        "schemas/invalid/test_invalid_hub_and_spoke_with_summary_confirmation.json"
    )
    validator = QuestionnaireValidator(_open_and_load_schema_file(filename))

    expected_errors = [{"message": error_messages.QUESTIONNAIRE_ONLY_ONE_PAGE}]

    validator.validate()

    assert validator.errors == expected_errors


def test_invalid_hub_and_spoke_and_summary_confirmation_non_existent():
    filename = "schemas/invalid/test_invalid_hub_and_spoke_and_summary_confirmation_non_existent.json"
    validator = QuestionnaireValidator(_open_and_load_schema_file(filename))

    expected_errors = [{"message": error_messages.QUESTIONNAIRE_MUST_CONTAIN_PAGE}]

    validator.validate()

    assert validator.errors == expected_errors


def test_invalid_repeating_section_list_name():
    filename = "schemas/invalid/test_invalid_repeating_section_list_name.json"
    validator = QuestionnaireValidator(_open_and_load_schema_file(filename))

    expected_errors = [
        {
            "message": error_messages.FOR_LIST_NEVER_POPULATED,
            "list_name": "non-existent-list",
        }
    ]

    validator.validate()

    assert validator.errors == expected_errors


def test_invalid_repeating_section_title_placeholders():
    filename = "schemas/invalid/test_invalid_repeating_section_title_placeholders.json"

    validator = QuestionnaireValidator(_open_and_load_schema_file(filename))

    expected_errors = [
        {
            "message": error_messages.PLACEHOLDERS_DONT_MATCH_DEFINITIONS,
            "text": "{person}",
            "differences": {"person"},
        }
    ]

    validator.validate()

    assert validator.errors == expected_errors


def test_invalid_hub_section_non_existent():
    filename = "schemas/invalid/test_invalid_hub_section_definition.json"

    validator = QuestionnaireValidator(_open_and_load_schema_file(filename))

    expected_error_message = {
        "message": error_messages.REQUIRED_HUB_SECTION_UNDEFINED,
        "required_section_id": "invalid-section-id",
    }

    validator.validate()

    assert expected_error_message == validator.errors[0]


def test_invalid_answer_action():
    filename = (
        "schemas/invalid/test_invalid_answer_action_redirect_to_list_add_question.json"
    )
    validator = QuestionnaireValidator(_open_and_load_schema_file(filename))

    expected_error_messages = [
        {
            "message": "List name defined in action params does not exist",
            "answer_id": "anyone-else-live-here-answer",
            "list_name": "non-existent-list-name",
        },
        {
            "message": "Block id defined in action params does not exist",
            "block_id": "non-existent-block-id",
            "answer_id": "anyone-else-live-here-answer",
        },
    ]

    validator.validate()

    assert expected_error_messages == validator.errors


def test_invalid_quotes_in_schema():
    filename = "schemas/invalid/test_invalid_quotes_in_schema_text.json"

    validator = QuestionnaireValidator(_open_and_load_schema_file(filename))

    expected_error_messages = [
        {"message": error_messages.DUMB_QUOTES_FOUND, "pointer": pointer}
        for pointer in [
            "/sections/0/groups/0/blocks/0/question/description",
            "/sections/0/groups/0/blocks/0/question/answers/0/guidance/contents/0/list/0",
            "/sections/0/groups/0/blocks/1/question_variants/0/question/title",
            "/sections/0/groups/0/blocks/0/question/answers/0/label",
        ]
    ]
    validator.validate_smart_quotes()

    assert validator.errors == expected_error_messages


def test_invalid_non_textfield_question_concatenation():
    filename = "schemas/invalid/test_invalid_question_concatenation_non_textfield.json"

    validator = QuestionnaireValidator(_open_and_load_schema_file(filename))

    expected_error_messages = [
        {
            "message": error_messages.SUMMARY_HAS_NON_TEXTFIELD_ANSWER,
            "answer_id": "checkbox-answer",
        }
    ]

    validator.validate()

    assert validator.errors == expected_error_messages
