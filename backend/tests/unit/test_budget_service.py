from app.services.budget_service import BudgetService

class TestCalculate:
    def test_basic_within_budget(self):
        calc = BudgetService.calculate(budget=10000, estimated_cost=8000, currency="INR")
        assert calc.budget == 10000.0
        assert calc.estimated_cost == 8000.0
        assert calc.remaining_budget == 2000.0
        assert calc.percentage_used == 80.0
        assert calc.is_over_budget is False

    def test_over_budget(self):
        calc = BudgetService.calculate(budget=10000, estimated_cost=12000, currency="INR")
        assert calc.remaining_budget == -2000.0
        assert calc.is_over_budget is True
        assert calc.percentage_used == 120.0

    def test_zero_budget(self):
        calc = BudgetService.calculate(budget=0, estimated_cost=500, currency="INR")
        assert calc.remaining_budget == -500.0
        assert calc.percentage_used == 0.0

    def test_full_utilization(self):
        calc = BudgetService.calculate(budget=5000, estimated_cost=5000, currency="USD")
        assert calc.remaining_budget == 0.0
        assert calc.percentage_used == 100.0
        assert calc.is_over_budget is False

    def test_currency_passthrough(self):
        calc = BudgetService.calculate(budget=5000, estimated_cost=2500, currency="EUR")
        assert calc.currency == "EUR"

    def test_rounding(self):
        calc = BudgetService.calculate(budget=3000, estimated_cost=1000.3333, currency="INR")
        assert calc.estimated_cost == 1000.33
        assert calc.remaining_budget == 1999.67


class TestAllocate:
    def test_home_allocations_sum_to_budget(self):
        allocs = BudgetService.allocate(budget=100000, planner_type="home")
        total = sum(a.allocated_amount for a in allocs)
        assert abs(total - 100000) < 1.0

    def test_party_allocations_have_catering(self):
        allocs = BudgetService.allocate(budget=50000, planner_type="party")
        names = [a.category.lower() for a in allocs]
        assert any("catering" in n or "food" in n for n in names)

    def test_jewelry_allocations_structure(self):
        allocs = BudgetService.allocate(budget=75000, planner_type="jewelry")
        assert len(allocs) > 0
        assert sum(a.percentage for a in allocs) == 100


class TestWarnings:
    def test_over_budget_strict(self):
        warnings = BudgetService.generate_warnings(
            budget=10000,
            estimated_cost=12000,
            flexibility="strict"
        )
        assert len(warnings) > 0

    def test_within_budget_no_warnings(self):
        warnings = BudgetService.generate_warnings(
            budget=10000,
            estimated_cost=8000,
            flexibility="strict"
        )
        assert len(warnings) == 0

    def test_flexible_tolerates_small_overage(self):
        warnings = BudgetService.generate_warnings(
            budget=10000,
            estimated_cost=10500,
            flexibility="flexible"
        )
        assert len(warnings) == 0

    def test_flexible_warns_on_large_overage(self):
        warnings = BudgetService.generate_warnings(
            budget=10000,
            estimated_cost=14000,
            flexibility="flexible"
        )
        assert len(warnings) > 0
