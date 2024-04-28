from datetime import datetime
from typing import Any, Generator

from .data import Data
from .scope import Scope
from ..template_data import PERSON
from ..template_scopes import SCOPE_GROUPS

import asyncio
import math
import re
last_scope_error_key: str = str()

class DataBuilder:
    

    def __init__(self, csv_data: dict):
        self.__csv_data = csv_data
        self.__storage = Data(data={"fo_cki": PERSON.copy()})
    
    @property
    def as_dict(self):
        return self.__storage.dict()

    def get_value_scopes(self, key: str, num: int = 0) -> Generator[Scope, Any, Any]: 
        
        data = re.search(r'(\D+)\.(\d{1,})$', key)
        if data:
            print("Bad key ", key)
            key = data.group(1)          # fix bug when some keys parsed as "key.number"
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

    async def build(self) -> None:
        for raw_key, value in self.__csv_data.items(): # (abc | abc1), Any
            if "Unnamed: " in raw_key:
                continue
            value = str(value)
            if value in [" ", "nan"]:
                continue
            if value.endswith(".0"):
                value = value[:-2]
            # await asyncio.sleep(0)
            for scope in self.get_value_scopes(raw_key):
                temp = self.__storage.data["fo_cki"]
                # print("scope location: ", raw_key, scope.location, scope.num)
                for data, key in self.find_by_scope(temp, scope.location, scope.num):
                    
                    if key == "vdate":
                        value = datetime.now().strftime("%Y-%m-%d")
                    data[key] = str(value)

   

            

    # def get_objects(self, parts: list[str], current: dict|list[dict], key: str, num: int) -> Generator[dict|list[dict]]:
    #     for i, part in enumerate(parts[:-1]): # "deals.0.deallife.0.dlsale_addr"
    #         current_type = list if part == "0" else dict
    #         if not isinstance(current, current_type): # VALIDATION TYPE
    #             print(f"IGNORED: {part} is not a valid key for {current} {current_type}")
    #             break
    #         if part == "0":
    #             if __num > 0 and i == 1:
    #                 current = current[__num]


    #         if num > 0:
    #             yield current[num-1]
    #         else:
    #             for item in current:
    #                 yield item
                    

            ####################
        #     if num > 0:
        #         yield current[num-1]
        #     else:
        #         for item in current:
        #             yield item
        #     ####################



        #     parts = path.split('.')
        #     if num == 0:
        #         # range(len(...))
        #     else:

                
        # if num > 0:
        #     ...

        # return scope



    # def build(self):
    #     for raw_key, value in self.__csv_data.items(): # (abc | abc1), Any
    #         for scope in self.get_value_scope(raw_key):
    #             ...


    #         scope = Scope.from_raw(key)
    #         for parts in scope.parts:
    #             parts = [
    #                 p.replace(".0.", f".{scope.num}.") for p in parts
    #             ]


    #         key, num = self.find_parts(key)   # abc, (0 | 1) 
    #         # для ключа "abc" находим с учетом num
    #         parts = self.get_value_scope(key, num)
    #         self.set_person_data(num, key, value)


    #         parts = [k.split('.') for k in KEYS[key]]
    #         for key_location in parts: # key locations in result object 
    #             current = self.__storage.data["fo_cki"] # result object with user data
    #             for sub_key in key_location.split("."):

    
    # def set_person_data(self, __num: int, __key: str, __value:Any) -> Generator[dict]:
    #     parts = [k.split('.') for k in KEYS[__key]]
    #     for part in parts:
                
    #         current = self.__storage["fo_cki"] # result object with user data

    #         # по каждому 

    #         def get_objects(self, part: list[str], current: dict|list[dict]):
    #             for i, key in enumerate(part[:-1]):

    #                 current_type = list if key == "0" else dict
    #                 if not isinstance(current, current_type): # VALIDATION TYPE
    #                     print(f"IGNORED: {key} is not a valid key for {current} {current_type}")
    #                     break
                    
    #                 if key == "0":
    #                     if __num > 0 and i == 1:
    #                         current = current[__num]

    #                         ...

                    
    #                 if key.isdigit() and __num > 0 and i == len(part)-2:
    #                     current[__num-1]
    #                 else:
    #                     ...

    #                 if not key.isdigit(): # if key not digit
    #                     current = current[key] 
    #                     continue
    #                 else:
    #                     if not isinstance(current, list): # VALIDATION TYPE
    #                         print(f"IGNORED: {key} is not a valid key for {current} list")
    #                         continue
    #                     if __num == 0 or i < len(part)-2:
    #                         current = current[__num]
    #                     else:
    #                         current = current[__num-1]
    #                         for cur in current:
    #                             for target in self.get_objects(
    #                                 part[i:], cur
    #                             ):
    #                                 yield target
    #                         break
    #             else:
    #                 yield current



    #         for key in part[:-1]: # until last KEY
    #             if key != "0":
    #                 current = current[key] 
    #             elif __num == -1:
    #                 for cur in current:
    #                     yield cur
    #             else:
    #                 current = current[__num]
    #             # if key not in current:
    #             #     current[key] = {}
                
    #         final_key = part[-1] # last KEY
    #         current[final_key] = __value

            ###############################

    # def update_nested_dict(d, keys, new_value):
    #     # Split the keys into a list of parts
    #     parts = [k.split('.') for k in keys]

    #     for part in parts:
    #         # Start at the root dictionary
    #         current = d
            
    #         # Traverse the dictionary path
    #         for key in part[:-1]:
    #             # If the key doesn't exist, create a new dictionary
    #             if key not in current:
    #                 current[key] = {}
    #             current = current[key]
            
    #         # Update the final key with the new value
    #         final_key = part[-1]
    #         current[final_key] = new_value

        
            # if parts := self.has_parts(key):
            #     key = parts.group(1)
            #     num = int(parts.group(2))
            #     # проверить есть ли такой num в обьекте


            # self[key] = value
