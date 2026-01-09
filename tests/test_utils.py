"""
tests for utility helpers and formatters
"""
from datetime import time
import pytest
from utils.type_mappings import is_room_type_compatible
from utils.formatters import (
    format_time_slot,
    format_time_short,
    parse_time,
    format_weekday_pl,
    format_parity_pl,
)
from app_config.constants import (
    ROOM_TYPE_LABELS_PL,
    COURSE_TYPE_LABELS_PL,
    WEEKDAY_LABELS_PL,
    WEEK_PARITY_LABELS_PL,
)


class TestTypeMappings:
    """tests for room/course compatibility mapping"""

    def test_room_type_compatible_exact_match(self):
        assert is_room_type_compatible('lecture', 'lecture_hall') is True

    def test_room_type_incompatible(self):
        assert is_room_type_compatible('computer_lab', 'lecture_hall') is False


class TestFormatters:
    """tests for formatting helpers"""

    def test_format_time_slot(self):
        result = format_time_slot(time(8, 0), time(9, 45))
        assert result == '08:00-09:45'

    def test_format_time_short(self):
        assert format_time_short(time(14, 30)) == '14:30'

    def test_parse_time_valid(self):
        assert parse_time('08:15') == time(8, 15)

    def test_parse_time_invalid(self):
        with pytest.raises(ValueError):
            parse_time('invalid')

    def test_format_weekday_pl(self):
        assert format_weekday_pl('monday') == WEEKDAY_LABELS_PL['monday']

    def test_format_parity_pl(self):
        assert format_parity_pl('odd') == WEEK_PARITY_LABELS_PL['odd']


class TestConstantsPresence:
    """basic sanity checks for config constants"""

    def test_constants_have_entries(self):
        assert ROOM_TYPE_LABELS_PL
        assert COURSE_TYPE_LABELS_PL
        assert WEEKDAY_LABELS_PL
        assert WEEK_PARITY_LABELS_PL