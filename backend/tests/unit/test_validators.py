import pytest
from app.services.image_service import ImageService
from app.core.exceptions import InvalidImageError

class TestValidateImage:
    def test_valid_jpeg(self):
        # JPEG magic bytes: FF D8 FF
        content = b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"A" * 100
        ImageService.validate_image(content, "image/jpeg", "test.jpg")

    def test_valid_png(self):
        # PNG magic bytes: 89 50 4E 47 0D 0A 1A 0A
        content = b"\x89PNG\r\n\x1a\n" + b"A" * 100
        ImageService.validate_image(content, "image/png", "test.png")

    def test_invalid_mime_type(self):
        content = b"PDF dummy content"
        with pytest.raises(InvalidImageError):
            ImageService.validate_image(content, "application/pdf", "test.pdf")

    def test_invalid_extension(self):
        content = b"\xff\xd8\xff\xe0\x00\x10JFIF"
        with pytest.raises(InvalidImageError):
            ImageService.validate_image(content, "image/jpeg", "test.exe")

    def test_file_too_large(self):
        content = b"\xff\xd8\xff" + b"0" * (11 * 1024 * 1024)
        with pytest.raises(InvalidImageError):
            ImageService.validate_image(content, "image/jpeg", "test.jpg")

    def test_empty_file(self):
        with pytest.raises(InvalidImageError):
            ImageService.validate_image(b"", "image/jpeg", "test.jpg")

    def test_bad_magic_bytes(self):
        # Mime claims jpeg but bytes are text
        content = b"Plain text file that is not a jpeg image"
        with pytest.raises(InvalidImageError):
            ImageService.validate_image(content, "image/jpeg", "fake.jpg")


class TestSanitizeFilename:
    def test_returns_uuid_based_name(self):
        name = ImageService.generate_filename("my-cool-photo.jpg")
        assert ".jpg" in name
        assert len(name) > 10

    def test_preserves_extension(self):
        name = ImageService.generate_filename("outfit.png")
        assert name.endswith(".png")

    def test_lowercase_extension(self):
        name = ImageService.generate_filename("outfit.JPEG")
        assert name.endswith(".jpeg") or name.endswith(".jpg")


class TestStoragePath:
    def test_with_plan_id(self):
        path = ImageService.get_storage_path(user_id="u1", plan_id="p1", filename="img.jpg")
        assert "u1" in path
        assert "img.jpg" in path

    def test_without_plan_id(self):
        path = ImageService.get_storage_path(user_id="u1", plan_id=None, filename="img.jpg")
        assert "u1" in path
        assert "img.jpg" in path
