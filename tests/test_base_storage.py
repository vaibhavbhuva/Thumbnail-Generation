import pytest
from abc import ABC, abstractmethod
from typing import Dict, Union, Optional

from app.libs.base_storage import Storage


def test_storage_is_abstract():
    """
    Verify that the Storage class is an abstract base class.
    """
    # Check if the class is registered as an ABC
    assert issubclass(Storage, ABC)
    # Check if it has abstract methods
    assert Storage.__abstractmethods__ is not None
    assert len(Storage.__abstractmethods__) > 0

def test_cannot_instantiate_abstract_storage():
    """
    Verify that attempting to instantiate the abstract Storage class raises a TypeError.
    """
    with pytest.raises(TypeError) as excinfo:
        Storage()
    assert "Can't instantiate abstract class Storage without an implementation for abstract methods 'public_url', 'write_file'" in str(excinfo.value)

def test_incomplete_subclass_cannot_be_instantiated():
    """
    Verify that a class inheriting from Storage but not implementing all
    abstract methods cannot be instantiated.
    """
    # Define a class that only implements one abstract method
    class IncompleteStorage(Storage):
        def write_file(
            self,
            file_path: str,
            file_content: Union[str, bytes],
            mime_type: Optional[str] = None,
        ):
            print("Writing file (incomplete implementation)")
            pass
        # public_url is not implemented

    with pytest.raises(TypeError) as excinfo:
        IncompleteStorage()

    # The error message should mention the missing abstract method(s)
    assert "Can't instantiate abstract class IncompleteStorage without an implementation for abstract method" in str(excinfo.value)
    assert "'public_url'" in str(excinfo.value) # Check if the missing method is mentioned

class InMemoryStorage(Storage):
    """
    A simple in-memory storage implementation for testing purposes.
    """
    def __init__(self):
        # Use a dictionary to simulate file storage
        self._files: Dict[str, Union[str, bytes]] = {}
        self._base_url = "http://localhost/files/" # Base URL for public access

    def write_file(
        self,
        file_path: str,
        file_content: Union[str, bytes],
        mime_type: Optional[str] = None, # mime_type is ignored in this simple example
    ):
        """
        Simulates writing a file to memory.
        """
        if not isinstance(file_path, str) or not file_path:
            raise ValueError("file_path must be a non-empty string")
        if not isinstance(file_content, (str, bytes)):
             raise ValueError("file_content must be a string or bytes")

        self._files[file_path] = file_content
        print(f"Simulated writing file: {file_path}") # Print for demonstration

    def public_url(self, file_path: str) -> str:
        """
        Generates a simulated public URL for the file.
        """
        if not isinstance(file_path, str) or not file_path:
            raise ValueError("file_path must be a non-empty string")

        # In a real implementation, you'd check if the file exists and
        # handle permissions. Here, we just generate the URL.
        # A more robust test implementation might check if the file_path
        # exists in self._files before generating the URL.
        return f"{self._base_url}{file_path}"

@pytest.fixture
def in_memory_storage():
    """
    Provides a fresh InMemoryStorage instance for each test.
    """
    return InMemoryStorage()

def test_in_memory_storage_is_concrete(in_memory_storage):
    """
    Verify that the InMemoryStorage class is a concrete implementation.
    """
    # Check that it's an instance of the concrete class
    assert isinstance(in_memory_storage, InMemoryStorage)
    # Check that it's a subclass of the abstract class
    assert isinstance(in_memory_storage, Storage)
    # Check that it has no abstract methods remaining
    assert not getattr(in_memory_storage, '__abstractmethods__', False)

def test_in_memory_storage_write_file(in_memory_storage):
    """
    Test the write_file method of the concrete storage.
    """
    file_path = "test/my_document.txt"
    file_content = "This is the content of the document."

    in_memory_storage.write_file(file_path, file_content)

    # In a real test, you'd verify the file was written correctly,
    # e.g., by adding a read_file method to the Storage ABC and its
    # implementation, and then asserting the content.
    # For this simple example, we'll just check if it was added to the internal dict.
    assert file_path in in_memory_storage._files
    assert in_memory_storage._files[file_path] == file_content

    # Test with bytes content
    file_path_bytes = "test/image.png"
    file_content_bytes = b"\x89PNG\r\n\x1a\n..." # Dummy bytes content
    in_memory_storage.write_file(file_path_bytes, file_content_bytes)
    assert file_path_bytes in in_memory_storage._files
    assert in_memory_storage._files[file_path_bytes] == file_content_bytes

    # Test error handling for write_file
    with pytest.raises(ValueError):
        in_memory_storage.write_file("", "content") # Empty file_path
    with pytest.raises(ValueError):
        in_memory_storage.write_file("path", 123) # Invalid content type

def test_in_memory_storage_public_url(in_memory_storage):
    """
    Test the public_url method of the concrete storage.
    This test will cover the 'pass' line in the abstract method's definition
    when running coverage on the concrete class's implementation.
    """
    file_path = "test/my_document.txt"
    expected_url = "http://localhost/files/test/my_document.txt"

    url = in_memory_storage.public_url(file_path)

    assert url == expected_url

    # Test error handling for public_url
    with pytest.raises(ValueError):
        in_memory_storage.public_url("") # Empty file_path