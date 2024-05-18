from datetime import datetime
from typing import Any, Generator

from .data import Data
from .scope import Scope
from config import PERSON, SCOPE_GROUPS, ADD_ZERO_TO_DNOM

import re
last_scope_error_key: str = str()

class DataBuilder:
    def __init__(self, csv_data: dict):
        self.__csv_data = csv_data
        self.__storage = Data(data={"fo_cki": PERSON.copy()})
    
    @property
    def as_dict(self) -> dict:
        return self.__storage.model_dump()

    def get_value_scopes(self, key: str, num: int = 0) -> Generator[Scope, Any, Any]: 
        data = re.search(r'(\D+)\.(\d{1,})$', key)
        if data:
            key = data.group(1)          # if key parsed as "key.number"
        data = re.search(r'(\D+)(\d{1,})$', key)
        if data:
            key = data.group(1)          # first part of raw key "abc1"
            num = int(data.group(2)) - 1 # offset to list indecses 
        if key.endswith("."):
            key = key[:-1]
        if key in SCOPE_GROUPS:
            scope_group = SCOPE_GROUPS[key]
            for scope_location in scope_group:
                yield Scope(num=num, location=scope_location.split("."))
        else:
            global last_scope_error_key
            if last_scope_error_key != key:
                last_scope_error_key = key
                print("#"*20)
                print(f"ERROR: no scope for key '{key}'")

    def find_by_scope(self, current: dict|list[dict], location: list, num: int)-> Generator[{dict, str}, Any, Any]:
        if len(location) == 1:
            yield current, location[0] # dict, str
        else:
            key = location[0]
            if key != "0":
                yield from self.find_by_scope(current[key], location[1:], num)
            elif num > -1:
                while len(current)-1 < num:
                    current.append(current[-1].copy())

                yield from self.find_by_scope(current[num], location[1:], num)
                num = 0 ########### 
            else:
                for item in current:
                    yield from self.find_by_scope(item, location[1:], num)

    def build(self) -> None:
        for raw_key, value in self.__csv_data.items(): # (abc | abc1), Any
            if "Unnamed: " in raw_key:
                continue
            value = str(value)
            if value in [" ", "nan"]:
                value = ""
            if value.endswith(".0"):
                value = value[:-2]
            for scope in self.get_value_scopes(raw_key):
                temp = self.__storage.data["fo_cki"]
                for data, key in self.find_by_scope(temp, scope.location, scope.num):
                    # logic for custom values 

                    if ADD_ZERO_TO_DNOM and key == "dnom":
                        value = "0"*(9 - len(value)) + value
                    if key == "lng":
                        data[key] = value or "1"
                    elif key == "cval":
                        if value.startswith("80"):
                            value = "3"+value
                    elif key == "vdate":
                        value = datetime.now().strftime("%Y-%m-%d")
                    elif key == "dlyear":
                        value = datetime.now().strftime("%Y")
                    elif key == "dlmonth":
                        value = datetime.now().strftime("%m")
                    data[key] = str(value) or data[key]

            
            for deal in self.__storage.data["fo_cki"]["deals"]:
                deal["deallife"][0]["dlyear"] = datetime.now().strftime("%Y")
                deal["deallife"][0]["dlmonth"] = datetime.now().strftime("%m")
                deal["deallife"][0]["dldateclc"] = datetime.now().strftime("%Y-%m-%d")
  