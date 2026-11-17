# Pick & Place UR3

Pick & Place vision system for the UR3 robot arm, it uses MobileNetV2, opencv and sklearn to classify and sort objects.
This project uses a custom tilting and vibrating plate to move objects around that are stuck together.


## How to run

1. Change the values in `settings.conf` to your liking.
2. Open a console in the project root.
3. Run `python -m pip install -e .` to install the project as a module to the active environment.
4. Run `client start` to start the Pick&Place client.

> [!NOTE]
> If you ran the client before with other paths set in settings.conf, they will not get automatically deleted.

## Documentation

Extensive documentation can be found in the documentation folder.

## License

Copyright (c) 2026 Tijn Klein Gunnewiek.

This project is licensed under the [PolyForm Noncommercial License 1.0.0](https://polyformproject.org). Anyone is welcome to view, run, and modify this code for personal, educational, or other non-commercial purposes, but commercial use and monetization are strictly prohibited without prior written permission.
