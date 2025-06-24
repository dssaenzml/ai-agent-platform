import base64
import json
import logging
from io import BytesIO

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import seaborn as sns
from pydantic import BaseModel, model_validator
from typing_extensions import Self

logger = logging.getLogger(__name__)


class SQLChartGeneratorToolWrapper(BaseModel):
    """
    Wrapper for generating charts and returning them as base64
    encoded strings.

    This class provides methods to generate a chart based on
    provided SQL results and return the chart as a base64 encoded string.

    Usage instructions:
    1. `pip install seaborn matplotlib pandas`
    2. Use the `run` method to create and retrieve the chart.
    """

    def preprocess_data(
        self,
        sql_result: str,
        chart_type: str,
    ) -> pd.DataFrame:
        """
        Preprocess the SQL result to ensure it is in a suitable format for plotting.

        :param sql_result: A JSON string containing the SQL result.
        :param chart_type: The type of chart to generate ('bar', 'line', or 'pie').
        :return: A pandas DataFrame ready for plotting.
        """
        data = json.loads(sql_result)
        df = pd.DataFrame(data)

        if df.empty:
            raise ValueError("The provided SQL result is empty.")

        if chart_type == "pie":
            if (len(df.index) > 1) and (len(df.columns) > 1):
                df["Category"] = df.iloc[:, :-1].apply(
                    lambda row: " / ".join(row.values.astype(str)),
                    axis=1,
                )
                df["Value"] = df[df.columns[-1]]
            else:
                raise ValueError("Insufficient data for pie chart.")
        else:
            # Ensure the first column is used as the index if it is not already
            if df.index.name is None:
                df = df.set_index(df.columns[0])

            # Handle cases where there is only one column of data
            if len(df.columns) == 1:
                df["Details"] = df.index
            else:
                df["Details"] = df.iloc[:, :-1].apply(
                    lambda row: " / ".join(row.values.astype(str)),
                    axis=1,
                )

        return df

    def generate_bar_chart(self, df: pd.DataFrame) -> str:
        """
        Generate a bart chart from the provided DataFrame and return it
        as a base64 encoded string.

        :param df: A pandas DataFrame containing the data to plot.
        :return: The base64 encoded string of the generated chart.
        """
        logger.info("---PLOTTING BAR CHART---")

        # Plotting the chart with seaborn
        plt.figure(figsize=(12, 8))
        sns.set_palette("muted")
        if len(df.columns) == 1:
            ax = sns.barplot(
                x=df.index,
                y=df[df.columns[0]],
                label=df.columns[0],
            )
        else:
            ax = sns.barplot(
                x=df.index,
                y=df[df.columns[-2]],
                hue=df["Details"],
            )

        # Formatting the plot
        ax.set_xlabel(df.index.name, fontsize=14)
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{int(x):,}"))
        plt.xticks(rotation=45)
        plt.legend(
            title="Details",
            bbox_to_anchor=(1.05, 1),
            loc="upper left",
        )
        plt.tight_layout()

        # Save the plot to a BytesIO object
        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)

        # Encode the image to base64
        chart_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        buffer.close()

        return chart_base64

    def generate_line_chart(self, df: pd.DataFrame) -> str:
        """
        Generate a line chart from the provided DataFrame and return
        it as a base64 encoded string.

        :param df: A pandas DataFrame containing the data to plot.
        :return: The base64 encoded string of the generated chart.
        """
        logger.info("---PLOTTING LINE CHART---")

        plt.figure(figsize=(12, 8))
        sns.set_palette("muted")
        if len(df.columns) == 1:
            ax = sns.lineplot(
                x=df.index,
                y=df[df.columns[0]],
                label=df.columns[0],
            )
        else:
            ax = sns.lineplot(
                x=df.index,
                y=df[df.columns[-2]],
                hue=df["Details"],
            )

        # Formatting the plot
        ax.set_xlabel(df.index.name, fontsize=14)
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{int(x):,}"))
        plt.xticks(rotation=45)
        plt.legend(
            title="Details",
            bbox_to_anchor=(1.05, 1),
            loc="upper left",
        )
        plt.tight_layout()

        # Save the plot to a BytesIO object
        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)

        # Encode the image to base64
        chart_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        buffer.close()

        return chart_base64

    def generate_pie_chart(self, df: pd.DataFrame) -> str:
        """
        Generate a pie chart from the provided DataFrame and
        return it as a base64 encoded string.

        :param df: A pandas DataFrame containing the data to plot.
        :return: The base64 encoded string of the generated chart.
        """
        logger.info("---PLOTTING PIE CHART---")

        category_column = df["Category"]
        value_column = df["Value"]

        # Plotting the pie chart
        plt.figure(figsize=(12, 8))
        plt.pie(
            value_column,
            labels=category_column,
            autopct="%1.1f%%",
            startangle=140,
            colors=sns.color_palette("muted"),
        )
        plt.axis("equal")
        plt.tight_layout()

        # Save the plot to a BytesIO object
        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)

        # Encode the image to base64
        chart_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        buffer.close()

        return chart_base64

    def run(
        self,
        sql_result: str,
        chart_type: str = "bar",
    ) -> str:
        """
        Run the process to generate a chart and return it as a base64
        encoded string.

        :param sql_result: A JSON string containing the SQL result.
        :param chart_type: The type of chart to generate ('bar', 'line', or 'pie').
        :return: The base64 encoded string of the generated chart.
        """
        try:
            df = self.preprocess_data(sql_result, chart_type)
            if chart_type == "line":
                return self.generate_line_chart(df)
            elif chart_type == "pie":
                return self.generate_pie_chart(df)
            else:
                return self.generate_bar_chart(df)
        except Exception as e:
            raise e
