"""
This module lets you get question and prediction information from Polymarket
via the API
"""
from typing import Dict, Generator

import requests

from fuzzy_search import search_question


class PolyQuestion:
    def __init__(self, poly: "Poly", data: Dict):
        """
            A Polymarket Question.
            :param poly:
            :param data:
            :ivar Poly poly:
            :ivar str api_url:
            :ivar int id:
            :ivar str question:
            :ivar str conditionID:
            :ivar str slug:
            :ivar str twitter_card_image:
            :ivar str resolution_source:
            :ivar str end_date:
            :ivar str category:
            :ivar str amm_type:
            :ivar str liquidity:
            :ivar str sponsor_name:
            :ivar str sponsor_image:
            :ivar str start_date:
            :ivar str x_axis_value:
            :ivar str y_axis_value:
            :ivar str denomination_token:
            :ivar str fee:
            :ivar str image:
            :ivar str icon:
            :ivar str lower_bound:
            :ivar str upper_bound:
            :ivar str description:
            :ivar str tags:
            :ivar list outcomes:
            :ivar list outcomePrices:
            :ivar str volume:
            :ivar bool active:
            :ivar str market_type:
            :ivar str format_type:
            :ivar str lower_bound_date:
            :ivar str upper_bound_date:
            :ivar bool closed:
            :ivar str marketMakerAddress:
            :ivar str created_at:
            :ivar str updated_at:
            :ivar str closed_time:
            :ivar bool wide_format:
            :ivar bool new:
            :ivar list use_cases:
        """
        self.poly = poly
        self._data = data
        self.api_url = f"{self.poly.api_url}?id={self.id}"

    def _get(self, url: str) -> requests.Response:
        """
        Send a get request to the Polymarket API.
        :param url:
        :return: response
        """
        r = self.poly.s.get(url)
        if r.status_code == 429:
            raise requests.RequestException("Hit API rate limit")
        return r

    def __getattr__(self, name: str):
        """
        If an attribute isn't directly on the class, check whether it's in the
        raw contract data.
        :param name:
        :return: attribute value
        """
        if name not in self._data:
            raise AttributeError(
                f"Attribute {name} is neither directly on this class nor in the raw question data"
            )
        return self._data[name]

    def refresh(self):
        """
        Refetch the market data from Polymarket,
        used when the question data might have changed.
        """
        r = self._get(self.api_url)
        self._data = r.json()[0]


class Poly:
    """
    The main class for interacting with Polymarket.
    """
    def __init__(self):
        self.api_url = "https://strapi-matic.poly.market/markets"
        self.s = requests.Session()
        self._data = self._get(self.api_url).json()

    def _get(self, url: str) -> requests.Response:
        """
        Send a get request to the Polymarket API.
        :param url:
        :return: response
        """
        r = self.s.get(url)
        if r.status_code == 429:
            raise requests.RequestException("Hit API rate limit")
        return r

    def refresh_markets(self):
        """
        Refetch all of the markets from the Polymarket API.
        """
        self._data = self._get(self.api_url).json()

    @property
    def questions(self) -> Generator[PolyQuestion, None, None]:
        """
        Generate all of the markets currently in Polymarket.
        :return: iterator of Polymarket questions
        """
        for data in self._data:
            yield PolyQuestion(self, data)

    def get_question(self, id: int) -> PolyQuestion:
        """
        Return the Polymarket question with the given id.
        :param id: market id
        :return: question
        """
        for data in self._data:
            if data["id"] == id:
                return PolyQuestion(self, data)
        raise ValueError("Unable to find a market with that ID.")

    def search_questions(self, guess: str) -> PolyQuestion:
        """
        Performs a fuzzy search on all of the Polymarket questions.
        Returns the question with the highest similarity.
        :param guess: guess string
        :return: market
        """
        return search_question(self, guess.lower())
