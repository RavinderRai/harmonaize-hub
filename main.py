import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Add the audiocraft submodule to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audiocraft'))

import streamlit as st
from src.app import set_page_configuration, main

if __name__ == "__main__":
    set_page_configuration()
    main()