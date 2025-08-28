import random
import streamlit as st
import pandas as pd
import numpy as np
st.title('Daily Wisdom From Proverbs')
proverbs = open('ProverbsADay/new_proverbs.txt','r')
pick = proverbs.readlines()
#print(pick)
scroll = random.choice(pick,replace=False)
print(scroll.strip('\n'))
proverbs.close()