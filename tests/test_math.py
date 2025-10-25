"""Tests for math engine."""

import pytest
from execution.math_engine import MathEngine


@pytest.fixture
def math_engine():
    """Create math engine fixture."""
    return MathEngine()


@pytest.mark.asyncio
async def test_basic_arithmetic(math_engine):
    """Test basic arithmetic."""
    result = await math_engine.evaluate("5 + 3")
    assert result['success']
    assert result['result'] == 8.0


@pytest.mark.asyncio
async def test_multiplication(math_engine):
    """Test multiplication."""
    result = await math_engine.evaluate("7 * 6")
    assert result['success']
    assert result['result'] == 42.0


@pytest.mark.asyncio
async def test_solve_equation(math_engine):
    """Test equation solving."""
    result = await math_engine.solve_equation("x^2 - 4 = 0", "x")
    assert result['success']
    assert len(result['solutions']) == 2
    assert 2.0 in result['solutions'] or -2.0 in result['solutions']


@pytest.mark.asyncio
async def test_differentiate(math_engine):
    """Test differentiation."""
    result = await math_engine.differentiate("x^2", "x")
    assert result['success']
    assert "2*x" in result['derivative']


@pytest.mark.asyncio
async def test_unit_conversion(math_engine):
    """Test unit conversion."""
    result = await math_engine.convert_units(100, "celsius", "fahrenheit")
    assert result['success']
    assert result['result'] == 212.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
