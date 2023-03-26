# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from pathlib import Path
from sqlalchemy import inspect, create_engine

class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    def myfunc(self):
        print("Hello my name is " + self.name)

p1 = Person("John", 36)
p1.myfunc()
