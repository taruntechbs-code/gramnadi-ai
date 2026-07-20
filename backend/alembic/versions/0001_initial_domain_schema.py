"""Create the initial GramNadi AI domain schema.

Revision ID: 0001_initial_domain_schema
Revises:
Create Date: 2026-07-20
"""

# flake8: noqa: E501

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial_domain_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    enterprise_type_enum = sa.Enum(
        "agriculture",
        "retail",
        "manufacturing",
        "services",
        "food_processing",
        "handicraft",
        "other",
        name="enterprise_type_enum",
    )
    sector_enum = sa.Enum(
        "agriculture",
        "retail",
        "manufacturing",
        "services",
        "food_and_beverage",
        "handicraft",
        "other",
        name="sector_enum",
    )
    loan_type_enum = sa.Enum(
        "term_loan",
        "working_capital",
        "microfinance",
        "kisan_credit_card",
        "other",
        name="loan_type_enum",
    )
    loan_status_enum = sa.Enum(
        "active", "closed", "overdue", "defaulted", "settled", name="loan_status_enum"
    )
    risk_level_enum = sa.Enum(
        "low", "medium", "high", "critical", name="risk_level_enum"
    )
    weather_condition_enum = sa.Enum(
        "clear", "cloudy", "rain", "storm", "haze", "other", name="weather_condition_enum"
    )
    intervention_type_enum = sa.Enum(
        "financial_counselling",
        "inventory_adjustment",
        "working_capital",
        "loan_restructuring",
        "market_linkage",
        "other",
        name="intervention_type_enum",
    )
    intervention_status_enum = sa.Enum(
        "planned", "in_progress", "completed", "cancelled", name="intervention_status_enum"
    )
    graph_node_type_enum = sa.Enum(
        "enterprise",
        "supplier",
        "customer",
        "market",
        "lender",
        "government_scheme",
        "other",
        name="graph_node_type_enum",
    )

    op.create_table(
        "enterprises",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("enterprise_code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("owner_name", sa.String(length=200), nullable=False),
        sa.Column("enterprise_type", enterprise_type_enum, nullable=False),
        sa.Column("district", sa.String(length=120), nullable=False),
        sa.Column("state", sa.String(length=120), nullable=False),
        sa.Column("village", sa.String(length=120), nullable=False),
        sa.Column("sector", sector_enum, nullable=False),
        sa.Column("business_start_date", sa.Date(), nullable=False),
        sa.Column("employees", sa.Integer(), nullable=False),
        sa.Column("annual_turnover", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("employees >= 0", name="ck_enterprises_employees_non_negative"),
        sa.CheckConstraint("annual_turnover >= 0", name="ck_enterprises_annual_turnover_non_negative"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("enterprise_code", name="uq_enterprises_enterprise_code"),
    )
    op.create_index("ix_enterprises_deleted_at", "enterprises", ["deleted_at"])
    op.create_index("ix_enterprises_location", "enterprises", ["state", "district", "village"])
    op.create_index("ix_enterprises_sector", "enterprises", ["sector"])

    op.create_table(
        "financial_records",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("enterprise_id", sa.Uuid(), nullable=False),
        sa.Column("month", sa.SmallInteger(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("income", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("expense", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("profit", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("savings", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("cash_balance", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("inventory_value", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("upi_transaction_count", sa.Integer(), nullable=False),
        sa.Column("upi_inflow", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("upi_outflow", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("month BETWEEN 1 AND 12", name="ck_financial_records_month"),
        sa.CheckConstraint("year BETWEEN 1900 AND 2100", name="ck_financial_records_year"),
        sa.CheckConstraint("income >= 0", name="ck_financial_records_income_non_negative"),
        sa.CheckConstraint("expense >= 0", name="ck_financial_records_expense_non_negative"),
        sa.CheckConstraint("savings >= 0", name="ck_financial_records_savings_non_negative"),
        sa.CheckConstraint("cash_balance >= 0", name="ck_financial_records_cash_balance_non_negative"),
        sa.CheckConstraint("inventory_value >= 0", name="ck_financial_records_inventory_value_non_negative"),
        sa.CheckConstraint("upi_transaction_count >= 0", name="ck_financial_records_upi_transaction_count_non_negative"),
        sa.CheckConstraint("upi_inflow >= 0", name="ck_financial_records_upi_inflow_non_negative"),
        sa.CheckConstraint("upi_outflow >= 0", name="ck_financial_records_upi_outflow_non_negative"),
        sa.ForeignKeyConstraint(["enterprise_id"], ["enterprises.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("enterprise_id", "month", "year", name="uq_financial_records_enterprise_month_year"),
    )
    op.create_index("ix_financial_records_deleted_at", "financial_records", ["deleted_at"])
    op.create_index("ix_financial_records_enterprise_period", "financial_records", ["enterprise_id", "year", "month"])

    op.create_table(
        "loans",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("enterprise_id", sa.Uuid(), nullable=False),
        sa.Column("loan_type", loan_type_enum, nullable=False),
        sa.Column("lender", sa.String(length=200), nullable=False),
        sa.Column("principal_amount", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("interest_rate", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("outstanding_amount", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("monthly_installment", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("next_due_date", sa.Date(), nullable=True),
        sa.Column("status", loan_status_enum, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("principal_amount >= 0", name="ck_loans_principal_amount_non_negative"),
        sa.CheckConstraint("interest_rate >= 0 AND interest_rate <= 100", name="ck_loans_interest_rate_range"),
        sa.CheckConstraint("outstanding_amount >= 0", name="ck_loans_outstanding_amount_non_negative"),
        sa.CheckConstraint("monthly_installment >= 0", name="ck_loans_monthly_installment_non_negative"),
        sa.ForeignKeyConstraint(["enterprise_id"], ["enterprises.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_loans_deleted_at", "loans", ["deleted_at"])
    op.create_index("ix_loans_enterprise_status", "loans", ["enterprise_id", "status"])

    op.create_table(
        "commodity_prices",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("commodity", sa.String(length=160), nullable=False),
        sa.Column("district", sa.String(length=120), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("price", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("price >= 0", name="ck_commodity_prices_price_non_negative"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("commodity", "district", "date", name="uq_commodity_prices_daily"),
    )
    op.create_index("ix_commodity_prices_deleted_at", "commodity_prices", ["deleted_at"])
    op.create_index("ix_commodity_prices_commodity_district_date", "commodity_prices", ["commodity", "district", "date"])

    op.create_table(
        "weather_snapshots",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("district", sa.String(length=120), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("temperature", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("rainfall", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("humidity", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("weather_condition", weather_condition_enum, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("temperature >= -90 AND temperature <= 70", name="ck_weather_snapshots_temperature_range"),
        sa.CheckConstraint("rainfall >= 0", name="ck_weather_snapshots_rainfall_non_negative"),
        sa.CheckConstraint("humidity >= 0 AND humidity <= 100", name="ck_weather_snapshots_humidity_range"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("district", "date", name="uq_weather_snapshots_district_date"),
    )
    op.create_index("ix_weather_snapshots_deleted_at", "weather_snapshots", ["deleted_at"])
    op.create_index("ix_weather_snapshots_district_date", "weather_snapshots", ["district", "date"])

    op.create_table(
        "predictions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("enterprise_id", sa.Uuid(), nullable=False),
        sa.Column("prediction_date", sa.Date(), nullable=False),
        sa.Column("cashflow_prediction", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("risk_score", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("risk_level", risk_level_enum, nullable=False),
        sa.Column("confidence_score", sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column("model_version", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("risk_score >= 0 AND risk_score <= 100", name="ck_predictions_risk_score_range"),
        sa.CheckConstraint("confidence_score >= 0 AND confidence_score <= 1", name="ck_predictions_confidence_score_range"),
        sa.ForeignKeyConstraint(["enterprise_id"], ["enterprises.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_predictions_deleted_at", "predictions", ["deleted_at"])
    op.create_index("ix_predictions_enterprise_date", "predictions", ["enterprise_id", "prediction_date"])

    op.create_table(
        "prediction_explanations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("prediction_id", sa.Uuid(), nullable=False),
        sa.Column("feature_name", sa.String(length=160), nullable=False),
        sa.Column("feature_importance", sa.Numeric(precision=7, scale=6), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("feature_importance >= -1 AND feature_importance <= 1", name="ck_prediction_explanations_importance_range"),
        sa.ForeignKeyConstraint(["prediction_id"], ["predictions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("prediction_id", "feature_name", name="uq_prediction_explanations_prediction_feature"),
    )
    op.create_index("ix_prediction_explanations_deleted_at", "prediction_explanations", ["deleted_at"])

    op.create_table(
        "interventions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("enterprise_id", sa.Uuid(), nullable=False),
        sa.Column("intervention_type", intervention_type_enum, nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("created_by", sa.String(length=200), nullable=False),
        sa.Column("status", intervention_status_enum, nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["enterprise_id"], ["enterprises.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_interventions_deleted_at", "interventions", ["deleted_at"])
    op.create_index("ix_interventions_enterprise_status", "interventions", ["enterprise_id", "status"])

    op.create_table(
        "counterfactual_simulations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("enterprise_id", sa.Uuid(), nullable=False),
        sa.Column("scenario_name", sa.String(length=200), nullable=False),
        sa.Column("modified_variable", sa.String(length=160), nullable=False),
        sa.Column("old_value", sa.JSON(), nullable=False),
        sa.Column("new_value", sa.JSON(), nullable=False),
        sa.Column("predicted_cashflow", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("predicted_risk", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("predicted_risk >= 0 AND predicted_risk <= 100", name="ck_counterfactual_simulations_predicted_risk_range"),
        sa.ForeignKeyConstraint(["enterprise_id"], ["enterprises.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_counterfactual_simulations_deleted_at", "counterfactual_simulations", ["deleted_at"])
    op.create_index("ix_counterfactual_simulations_enterprise", "counterfactual_simulations", ["enterprise_id"])

    op.create_table(
        "village_graph_nodes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("enterprise_id", sa.Uuid(), nullable=False),
        sa.Column("node_type", graph_node_type_enum, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["enterprise_id"], ["enterprises.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_village_graph_nodes_deleted_at", "village_graph_nodes", ["deleted_at"])
    op.create_index("ix_village_graph_nodes_enterprise", "village_graph_nodes", ["enterprise_id"])

    op.create_table(
        "village_graph_edges",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("source_node", sa.Uuid(), nullable=False),
        sa.Column("target_node", sa.Uuid(), nullable=False),
        sa.Column("relationship", sa.String(length=120), nullable=False),
        sa.Column("weight", sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("source_node <> target_node", name="ck_village_graph_edges_distinct_nodes"),
        sa.CheckConstraint("weight >= 0", name="ck_village_graph_edges_weight_non_negative"),
        sa.ForeignKeyConstraint(["source_node"], ["village_graph_nodes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_node"], ["village_graph_nodes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_node", "target_node", "relationship", name="uq_village_graph_edges_connection"),
    )
    op.create_index("ix_village_graph_edges_deleted_at", "village_graph_edges", ["deleted_at"])
    op.create_index("ix_village_graph_edges_source_target", "village_graph_edges", ["source_node", "target_node"])


def downgrade() -> None:
    op.drop_index("ix_village_graph_edges_source_target", table_name="village_graph_edges")
    op.drop_index("ix_village_graph_edges_deleted_at", table_name="village_graph_edges")
    op.drop_table("village_graph_edges")
    op.drop_index("ix_village_graph_nodes_enterprise", table_name="village_graph_nodes")
    op.drop_index("ix_village_graph_nodes_deleted_at", table_name="village_graph_nodes")
    op.drop_table("village_graph_nodes")
    op.drop_index("ix_counterfactual_simulations_enterprise", table_name="counterfactual_simulations")
    op.drop_index("ix_counterfactual_simulations_deleted_at", table_name="counterfactual_simulations")
    op.drop_table("counterfactual_simulations")
    op.drop_index("ix_interventions_enterprise_status", table_name="interventions")
    op.drop_index("ix_interventions_deleted_at", table_name="interventions")
    op.drop_table("interventions")
    op.drop_index("ix_prediction_explanations_deleted_at", table_name="prediction_explanations")
    op.drop_table("prediction_explanations")
    op.drop_index("ix_predictions_enterprise_date", table_name="predictions")
    op.drop_index("ix_predictions_deleted_at", table_name="predictions")
    op.drop_table("predictions")
    op.drop_index("ix_weather_snapshots_district_date", table_name="weather_snapshots")
    op.drop_index("ix_weather_snapshots_deleted_at", table_name="weather_snapshots")
    op.drop_table("weather_snapshots")
    op.drop_index("ix_commodity_prices_commodity_district_date", table_name="commodity_prices")
    op.drop_index("ix_commodity_prices_deleted_at", table_name="commodity_prices")
    op.drop_table("commodity_prices")
    op.drop_index("ix_loans_enterprise_status", table_name="loans")
    op.drop_index("ix_loans_deleted_at", table_name="loans")
    op.drop_table("loans")
    op.drop_index("ix_financial_records_enterprise_period", table_name="financial_records")
    op.drop_index("ix_financial_records_deleted_at", table_name="financial_records")
    op.drop_table("financial_records")
    op.drop_index("ix_enterprises_sector", table_name="enterprises")
    op.drop_index("ix_enterprises_location", table_name="enterprises")
    op.drop_index("ix_enterprises_deleted_at", table_name="enterprises")
    op.drop_table("enterprises")

    for enum_name in (
        "graph_node_type_enum",
        "intervention_status_enum",
        "intervention_type_enum",
        "weather_condition_enum",
        "risk_level_enum",
        "loan_status_enum",
        "loan_type_enum",
        "sector_enum",
        "enterprise_type_enum",
    ):
        op.execute(sa.text(f"DROP TYPE IF EXISTS {enum_name}"))
