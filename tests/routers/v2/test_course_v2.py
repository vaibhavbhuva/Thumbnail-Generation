from fastapi.testclient import TestClient
from unittest.mock import MagicMock, Mock

from app.models import ImageVariationResponse, LogoDetection


def test_generate_course_image_variations_success(client: TestClient , mocker):
    """
    Tests the successful response of the generate_course_image_variations endpoint.
    """
    course_id = "do_1234567890"
    mock_image_urls = ["url1.jpg", "url2.png"]
    mock_logo_detection_data = {"found": True, "warning": None}

    mock_generate_variations = mocker.patch(
        "app.routers.v2.course.generate_image_variations",
        return_value=(mock_logo_detection_data, mock_image_urls)
    )

    # Mock logger.info
    mock_logger_info = mocker.patch("app.routers.v2.course.logger")

    response = client.get(f"/v2/image/variations/course/{course_id}")

    # Assert the status code is 200 OK
    assert response.status_code == 200

    expected_response_model = ImageVariationResponse(
        images=mock_image_urls,
        logo=LogoDetection(**mock_logo_detection_data)
    )

    assert response.json() == expected_response_model.model_dump()

    # Assert the service function was called with the correct course_id
    mock_generate_variations.assert_called_once_with(course_id)

    # Assert logger.info was called
    mock_logger_info.info.assert_called_once_with(f"Course ID : {course_id}")

def test_generate_course_image_variations_failed_without_params(client: TestClient , mocker):
    """
    Tests the successful response of the generate_course_image_variations endpoint.
    """
    course_id = ""
    mock_image_urls = ["url1.jpg", "url2.png"]
    mock_logo_detection_data = {"found": True, "warning": None}

    mock_generate_variations = mocker.patch(
        "app.routers.v2.course.generate_image_variations",
        return_value=(mock_logo_detection_data, mock_image_urls)
    )

    response = client.get(f"/v2/image/variations/course/{course_id}")

    # Assert the status code is 200 OK
    assert response.status_code == 404

    expected_response_model = {'detail': 'Not Found'}

    assert response.json() == expected_response_model

    # Assert the service function was not called when course id is empty
    mock_generate_variations.assert_not_called()

def test_generate_course_image_variations_exception_handling(client: TestClient, mocker):
    """
    Tests the exception handling path of the generate_course_image_variations endpoint.
    """
    course_id = "do_1234567890"

    def broken_generate_image(resource_id: str):
            raise Exception("Simulated error")

    mock_generate_variations = mocker.patch(
        "app.routers.v2.course.generate_image_variations",
        side_effect = broken_generate_image
    )

    # Mock logger.exception
    mock_logger_exception = mocker.patch("app.routers.v2.course.logger")

    response = client.get(f"/v2/image/variations/course/{course_id}")

    # Assert the status code is 500 Internal Server Error
    assert response.status_code == 500

    assert response.json() == {
        "detail": "Something went wrong, please try again later..."
    }
    # Assert the service function was called with the correct course_id
    mock_generate_variations.assert_called_once_with(course_id)

    # Assert logger.exception was called
    mock_logger_exception.exception.assert_called_once_with("Error while generating the image variations")