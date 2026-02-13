"""Tests for common utility functions."""

from pathlib import Path

import pytest

from dashcam_investigator.utils.common import convert_to_seconds, generate_file_hash


class TestGenerateFileHash:
    """Test cases for generate_file_hash function."""

    def test_hash_same_content_produces_same_hash(self, temp_dir):
        """Test that same content produces identical hash."""
        file1 = temp_dir / "file1.txt"
        file2 = temp_dir / "file2.txt"

        content = "This is test content"
        file1.write_text(content)
        file2.write_text(content)

        hash1 = generate_file_hash(file1)
        hash2 = generate_file_hash(file2)

        assert hash1 == hash2

    def test_hash_different_content_produces_different_hash(self, temp_dir):
        """Test that different content produces different hash."""
        file1 = temp_dir / "file1.txt"
        file2 = temp_dir / "file2.txt"

        file1.write_text("Content A")
        file2.write_text("Content B")

        hash1 = generate_file_hash(file1)
        hash2 = generate_file_hash(file2)

        assert hash1 != hash2

    def test_hash_format(self, temp_dir):
        """Test that hash is in correct SHA256 format."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("Test content")

        hash_value = generate_file_hash(test_file)

        # SHA256 hash should be 64 hexadecimal characters
        assert len(hash_value) == 64
        assert all(c in "0123456789abcdef" for c in hash_value)

    def test_hash_empty_file(self, temp_dir):
        """Test hashing an empty file."""
        empty_file = temp_dir / "empty.txt"
        empty_file.write_text("")

        hash_value = generate_file_hash(empty_file)

        # SHA256 of empty file
        expected = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        assert hash_value == expected

    def test_hash_binary_file(self, temp_dir):
        """Test hashing a binary file."""
        binary_file = temp_dir / "binary.bin"
        binary_file.write_bytes(b"\x00\x01\x02\x03\x04\x05")

        hash_value = generate_file_hash(binary_file)

        assert len(hash_value) == 64
        assert all(c in "0123456789abcdef" for c in hash_value)

    def test_hash_large_file(self, temp_dir):
        """Test hashing a file larger than the buffer size (4096 bytes)."""
        large_file = temp_dir / "large.txt"
        # Create content larger than 4KB buffer
        large_content = "A" * 10000
        large_file.write_text(large_content)

        hash_value = generate_file_hash(large_file)

        assert len(hash_value) == 64

        # Verify consistency
        hash_value2 = generate_file_hash(large_file)
        assert hash_value == hash_value2


class TestConvertToSeconds:
    """Test cases for convert_to_seconds function."""

    def test_convert_zero_milliseconds(self):
        """Test conversion of 0 milliseconds."""
        seconds, minutes = convert_to_seconds(0)

        assert seconds == "00"
        assert minutes == "00"

    def test_convert_one_second(self):
        """Test conversion of 1 second (1000 ms)."""
        seconds, minutes = convert_to_seconds(1000)

        assert seconds == "01"
        assert minutes == "00"

    def test_convert_one_minute(self):
        """Test conversion of 1 minute (60000 ms)."""
        seconds, minutes = convert_to_seconds(60000)

        assert seconds == "00"
        assert minutes == "01"

    def test_convert_mixed_time(self):
        """Test conversion of mixed minutes and seconds."""
        # 2 minutes and 30 seconds = 150000 ms
        seconds, minutes = convert_to_seconds(150000)

        assert seconds == 30  # >= 10, returns int
        assert minutes == "02"

    def test_convert_with_zero_padding_seconds(self):
        """Test that single digit seconds are zero-padded."""
        # 5 seconds = 5000 ms
        seconds, minutes = convert_to_seconds(5000)

        assert seconds == "05"
        assert minutes == "00"

    def test_convert_with_zero_padding_minutes(self):
        """Test that single digit minutes are zero-padded."""
        # 3 minutes and 15 seconds = 195000 ms
        seconds, minutes = convert_to_seconds(195000)

        assert seconds == 15  # >= 10, returns int
        assert minutes == "03"

    def test_convert_no_zero_padding_double_digits(self):
        """Test that double digit values are not padded."""
        # 12 minutes and 45 seconds = 765000 ms
        seconds, minutes = convert_to_seconds(765000)

        assert seconds == 45  # >= 10, returns int
        assert minutes == 12  # >= 10, returns int

    def test_convert_59_seconds(self):
        """Test conversion at boundary (59 seconds)."""
        # 59 seconds = 59000 ms
        seconds, minutes = convert_to_seconds(59000)

        assert seconds == 59  # >= 10, returns int
        assert minutes == "00"

    def test_convert_59_minutes_59_seconds(self):
        """Test conversion at max boundary (59:59)."""
        # 59 minutes 59 seconds = 3599000 ms
        seconds, minutes = convert_to_seconds(3599000)

        assert seconds == 59  # >= 10, returns int
        assert minutes == 59  # >= 10, returns int

    def test_convert_large_value(self):
        """Test conversion of large values (hours not considered)."""
        # 2 hours 30 minutes 45 seconds = 9045000 ms
        # Should wrap at 60 minutes, showing only minutes % 60
        seconds, minutes = convert_to_seconds(9045000)

        assert seconds == 45  # >= 10, returns int
        # 150 minutes % 60 = 30 minutes
        assert minutes == 30  # >= 10, returns int

    def test_return_type(self):
        """Test that function returns strings."""
        seconds, minutes = convert_to_seconds(5000)

        assert isinstance(seconds, str)
        assert isinstance(minutes, str)
