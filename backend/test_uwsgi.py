#!/usr/bin/env python

from app import create_app
from optimal_mod.modcontroller import test

app = create_app()
#test()

if __name__ == "__main__":
    app.run()