const DEMO_DATA = {
  "version": "demo_selected_events_8x4",
  "trajectoryRows": [
    {
      "event": "snoring",
      "basePrompt": "snoring",
      "variants": [
        {
          "id": "demo_00_snoring_static",
          "trajectoryKey": "static",
          "trajectoryLabel": "Static",
          "prompt": "snoring stationary very close behind-left, above ear level.",
          "spatialPhrase": "stationary very close behind-left, above ear level",
          "waypoints": [
            [
              0.0,
              120.0,
              20.0,
              0.8
            ],
            [
              10.0,
              120.0,
              20.0,
              0.8
            ]
          ],
          "audio": "audio/demo_latest/physwave/demo_00_snoring_static.wav"
        },
        {
          "id": "demo_00_snoring_linear",
          "trajectoryKey": "linear",
          "trajectoryLabel": "Linear",
          "prompt": "snoring moving gently in a straight line from left to front-left.",
          "spatialPhrase": "moving gently in a straight line from left to front-left",
          "waypoints": [
            [
              0.0,
              95.0,
              15.0,
              1.2
            ],
            [
              1.25,
              88.413,
              15.851,
              1.137
            ],
            [
              2.5,
              81.102,
              16.555,
              1.09
            ],
            [
              3.75,
              73.213,
              17.026,
              1.061
            ],
            [
              5.0,
              65.0,
              17.192,
              1.051
            ],
            [
              6.25,
              56.787,
              17.026,
              1.061
            ],
            [
              7.5,
              48.898,
              16.555,
              1.09
            ],
            [
              8.75,
              41.587,
              15.851,
              1.137
            ],
            [
              10.0,
              35.0,
              15.0,
              1.2
            ]
          ],
          "audio": "audio/demo_latest/physwave/demo_00_snoring_linear.wav"
        },
        {
          "id": "demo_00_snoring_approach_recede",
          "trajectoryKey": "approach_recede",
          "trajectoryLabel": "Approach / Recede",
          "prompt": "snoring receding behind-left from close to far.",
          "spatialPhrase": "receding behind-left from close to far",
          "waypoints": [
            [
              0.0,
              130.0,
              20.0,
              0.8
            ],
            [
              10.0,
              130.0,
              20.0,
              8.0
            ]
          ],
          "audio": "audio/demo_latest/physwave/demo_00_snoring_approach_recede.wav"
        },
        {
          "id": "demo_00_snoring_circular",
          "trajectoryKey": "circular",
          "trajectoryLabel": "Circular",
          "prompt": "snoring circling from front-left toward rear-right.",
          "spatialPhrase": "circling from front-left toward rear-right",
          "waypoints": [
            [
              0.0,
              55.0,
              0.0,
              4.0
            ],
            [
              1.25,
              33.125,
              0.0,
              4.0
            ],
            [
              2.5,
              11.25,
              0.0,
              4.0
            ],
            [
              3.75,
              -10.625,
              0.0,
              4.0
            ],
            [
              5.0,
              -32.5,
              0.0,
              4.0
            ],
            [
              6.25,
              -54.375,
              0.0,
              4.0
            ],
            [
              7.5,
              -76.25,
              0.0,
              4.0
            ],
            [
              8.75,
              -98.125,
              0.0,
              4.0
            ],
            [
              10.0,
              -120.0,
              0.0,
              4.0
            ]
          ],
          "audio": "audio/demo_latest/physwave/demo_00_snoring_circular.wav"
        }
      ]
    },
    {
      "event": "keyboard",
      "basePrompt": "keyboard typing",
      "variants": [
        {
          "id": "demo_01_keyboard_static",
          "trajectoryKey": "static",
          "trajectoryLabel": "Static",
          "prompt": "keyboard typing stationary nearby at front-left.",
          "spatialPhrase": "stationary nearby at front-left",
          "waypoints": [
            [
              0.0,
              35.0,
              0.0,
              1.8
            ],
            [
              10.0,
              35.0,
              0.0,
              1.8
            ]
          ],
          "audio": "audio/demo_latest/physwave/demo_01_keyboard_static.wav"
        },
        {
          "id": "demo_01_keyboard_linear",
          "trajectoryKey": "linear",
          "trajectoryLabel": "Linear",
          "prompt": "keyboard typing moving in a straight line from the right side to the left side.",
          "spatialPhrase": "moving in a straight line from the right side to the left side",
          "waypoints": [
            [
              0.0,
              -70.0,
              0.0,
              2.2
            ],
            [
              1.25,
              -64.113,
              0.0,
              1.723
            ],
            [
              2.5,
              -53.948,
              0.0,
              1.279
            ],
            [
              3.75,
              -34.484,
              0.0,
              0.913
            ],
            [
              5.0,
              0.0,
              0.0,
              0.752
            ],
            [
              6.25,
              34.484,
              0.0,
              0.913
            ],
            [
              7.5,
              53.948,
              0.0,
              1.279
            ],
            [
              8.75,
              64.113,
              0.0,
              1.723
            ],
            [
              10.0,
              70.0,
              0.0,
              2.2
            ]
          ],
          "audio": "audio/demo_latest/physwave/demo_01_keyboard_linear.wav"
        },
        {
          "id": "demo_01_keyboard_approach_recede",
          "trajectoryKey": "approach_recede",
          "trajectoryLabel": "Approach / Recede",
          "prompt": "keyboard typing approaching from the front-right to the desk.",
          "spatialPhrase": "approaching from the front-right to the desk",
          "waypoints": [
            [
              0.0,
              -25.0,
              0.0,
              7.5
            ],
            [
              10.0,
              -25.0,
              0.0,
              0.9
            ]
          ],
          "audio": "audio/demo_latest/physwave/demo_01_keyboard_approach_recede.wav"
        },
        {
          "id": "demo_01_keyboard_circular",
          "trajectoryKey": "circular",
          "trajectoryLabel": "Circular",
          "prompt": "keyboard typing circling across the front half of the listener.",
          "spatialPhrase": "circling across the front half of the listener",
          "waypoints": [
            [
              0.0,
              -60.0,
              0.0,
              2.0
            ],
            [
              1.25,
              -44.375,
              0.0,
              2.0
            ],
            [
              2.5,
              -28.75,
              0.0,
              2.0
            ],
            [
              3.75,
              -13.125,
              0.0,
              2.0
            ],
            [
              5.0,
              2.5,
              0.0,
              2.0
            ],
            [
              6.25,
              18.125,
              0.0,
              2.0
            ],
            [
              7.5,
              33.75,
              0.0,
              2.0
            ],
            [
              8.75,
              49.375,
              0.0,
              2.0
            ],
            [
              10.0,
              65.0,
              0.0,
              2.0
            ]
          ],
          "audio": "audio/demo_latest/physwave/demo_01_keyboard_circular.wav"
        }
      ]
    },
    {
      "event": "whistle",
      "basePrompt": "whistle",
      "variants": [
        {
          "id": "demo_02_whistle_static",
          "trajectoryKey": "static",
          "trajectoryLabel": "Static",
          "prompt": "whistle stationary behind-right, slightly below ear level.",
          "spatialPhrase": "stationary behind-right, slightly below ear level",
          "waypoints": [
            [
              0.0,
              -120.0,
              -10.0,
              2.0
            ],
            [
              10.0,
              -120.0,
              -10.0,
              2.0
            ]
          ],
          "audio": "audio/demo_latest/physwave/demo_02_whistle_static.wav"
        },
        {
          "id": "demo_02_whistle_linear",
          "trajectoryKey": "linear",
          "trajectoryLabel": "Linear",
          "prompt": "whistle moving in a straight line from behind-right to front-left.",
          "spatialPhrase": "moving in a straight line from behind-right to front-left",
          "waypoints": [
            [
              0.0,
              -125.0,
              -10.0,
              2.6
            ],
            [
              1.25,
              -123.317,
              -11.62,
              1.961
            ],
            [
              2.5,
              -119.962,
              -14.76,
              1.329
            ],
            [
              3.75,
              -110.185,
              -23.082,
              0.72
            ],
            [
              5.0,
              -35.0,
              -45.0,
              0.319
            ],
            [
              6.25,
              31.211,
              -13.605,
              0.72
            ],
            [
              7.5,
              40.185,
              -4.872,
              1.329
            ],
            [
              8.75,
              43.376,
              -1.649,
              1.961
            ],
            [
              10.0,
              45.0,
              0.0,
              2.6
            ]
          ],
          "audio": "audio/demo_latest/physwave/demo_02_whistle_linear.wav"
        },
        {
          "id": "demo_02_whistle_approach_recede",
          "trajectoryKey": "approach_recede",
          "trajectoryLabel": "Approach / Recede",
          "prompt": "whistle receding behind-right from nearby to far away.",
          "spatialPhrase": "receding behind-right from nearby to far away",
          "waypoints": [
            [
              0.0,
              -120.0,
              -10.0,
              2.0
            ],
            [
              10.0,
              -120.0,
              -10.0,
              14.0
            ]
          ],
          "audio": "audio/demo_latest/physwave/demo_02_whistle_approach_recede.wav"
        },
        {
          "id": "demo_02_whistle_circular",
          "trajectoryKey": "circular",
          "trajectoryLabel": "Circular",
          "prompt": "whistle circling from the right side to the rear-left.",
          "spatialPhrase": "circling from the right side to the rear-left",
          "waypoints": [
            [
              0.0,
              -90.0,
              0.0,
              2.4
            ],
            [
              1.25,
              -106.875,
              0.0,
              2.4
            ],
            [
              2.5,
              -123.75,
              0.0,
              2.4
            ],
            [
              3.75,
              -140.625,
              0.0,
              2.4
            ],
            [
              5.0,
              -157.5,
              0.0,
              2.4
            ],
            [
              6.25,
              -174.375,
              0.0,
              2.4
            ],
            [
              7.5,
              168.75,
              0.0,
              2.4
            ],
            [
              8.75,
              151.875,
              0.0,
              2.4
            ],
            [
              10.0,
              135.0,
              0.0,
              2.4
            ]
          ],
          "audio": "audio/demo_latest/physwave/demo_02_whistle_circular.wav"
        }
      ]
    },
    {
      "event": "motorcycle engine",
      "basePrompt": "motorcycle engine",
      "variants": [
        {
          "id": "demo_03_motorcycle_engine_static",
          "trajectoryKey": "static",
          "trajectoryLabel": "Static",
          "prompt": "motorcycle engine stationary at front-left.",
          "spatialPhrase": "stationary at front-left",
          "waypoints": [
            [
              0.0,
              35.0,
              0.0,
              1.8
            ],
            [
              10.0,
              35.0,
              0.0,
              1.8
            ]
          ],
          "audio": "audio/demo_latest/physwave/demo_03_motorcycle_engine_static.wav"
        },
        {
          "id": "demo_03_motorcycle_engine_linear",
          "trajectoryKey": "linear",
          "trajectoryLabel": "Linear",
          "prompt": "motorcycle engine passing in a straight line from the left side to the right side.",
          "spatialPhrase": "passing in a straight line from the left side to the right side",
          "waypoints": [
            [
              0.0,
              75.0,
              0.0,
              4.0
            ],
            [
              1.25,
              70.34,
              0.0,
              3.077
            ],
            [
              2.5,
              61.813,
              0.0,
              2.192
            ],
            [
              3.75,
              43.015,
              0.0,
              1.416
            ],
            [
              5.0,
              0.0,
              0.0,
              1.035
            ],
            [
              6.25,
              -43.015,
              0.0,
              1.416
            ],
            [
              7.5,
              -61.813,
              0.0,
              2.192
            ],
            [
              8.75,
              -70.34,
              0.0,
              3.077
            ],
            [
              10.0,
              -75.0,
              0.0,
              4.0
            ]
          ],
          "audio": "audio/demo_latest/physwave/demo_03_motorcycle_engine_linear.wav"
        },
        {
          "id": "demo_03_motorcycle_engine_approach_recede",
          "trajectoryKey": "approach_recede",
          "trajectoryLabel": "Approach / Recede",
          "prompt": "motorcycle engine approaching from behind-right from far away to very close.",
          "spatialPhrase": "approaching from behind-right from far away to very close",
          "waypoints": [
            [
              0.0,
              -122.0,
              0.0,
              15.0
            ],
            [
              10.0,
              -122.0,
              0.0,
              1.0
            ]
          ],
          "audio": "audio/demo_latest/physwave/demo_03_motorcycle_engine_approach_recede.wav"
        },
        {
          "id": "demo_03_motorcycle_engine_circular",
          "trajectoryKey": "circular",
          "trajectoryLabel": "Circular",
          "prompt": "motorcycle engine circling from rear-left to front-right.",
          "spatialPhrase": "circling from rear-left to front-right",
          "waypoints": [
            [
              0.0,
              145.0,
              0.0,
              3.6
            ],
            [
              1.25,
              121.25,
              0.0,
              3.6
            ],
            [
              2.5,
              97.5,
              0.0,
              3.6
            ],
            [
              3.75,
              73.75,
              0.0,
              3.6
            ],
            [
              5.0,
              50.0,
              0.0,
              3.6
            ],
            [
              6.25,
              26.25,
              0.0,
              3.6
            ],
            [
              7.5,
              2.5,
              0.0,
              3.6
            ],
            [
              8.75,
              -21.25,
              0.0,
              3.6
            ],
            [
              10.0,
              -45.0,
              0.0,
              3.6
            ]
          ],
          "audio": "audio/demo_latest/physwave/demo_03_motorcycle_engine_circular.wav"
        }
      ]
    },
    {
      "event": "dog barking",
      "basePrompt": "dog bark",
      "variants": [
        {
          "id": "demo_04_dog_barking_static",
          "trajectoryKey": "static",
          "trajectoryLabel": "Static",
          "prompt": "dog bark stationary at the front-right, near ear level.",
          "spatialPhrase": "stationary at the front-right, near ear level",
          "waypoints": [
            [
              0.0,
              -40.0,
              10.0,
              1.0
            ],
            [
              10.0,
              -40.0,
              10.0,
              1.0
            ]
          ],
          "audio": "audio/demo_latest/physwave/demo_04_dog_barking_static.wav"
        },
        {
          "id": "demo_04_dog_barking_linear",
          "trajectoryKey": "linear",
          "trajectoryLabel": "Linear",
          "prompt": "dog bark moving in a straight line from the rear-right to the front.",
          "spatialPhrase": "moving in a straight line from the rear-right to the front",
          "waypoints": [
            [
              0.0,
              -140.0,
              0.0,
              1.2
            ],
            [
              1.25,
              -136.77,
              0.0,
              0.91
            ],
            [
              2.5,
              -130.575,
              0.0,
              0.627
            ],
            [
              3.75,
              -114.804,
              0.0,
              0.362
            ],
            [
              5.0,
              -60.0,
              0.0,
              0.208
            ],
            [
              6.25,
              -5.196,
              0.0,
              0.362
            ],
            [
              7.5,
              10.575,
              0.0,
              0.627
            ],
            [
              8.75,
              16.77,
              0.0,
              0.91
            ],
            [
              10.0,
              20.0,
              0.0,
              1.2
            ]
          ],
          "audio": "audio/demo_latest/physwave/demo_04_dog_barking_linear.wav"
        },
        {
          "id": "demo_04_dog_barking_approach_recede",
          "trajectoryKey": "approach_recede",
          "trajectoryLabel": "Approach / Recede",
          "prompt": "dog bark receding from nearby to far away on the left side.",
          "spatialPhrase": "receding from nearby to far away on the left side",
          "waypoints": [
            [
              0.0,
              82.0,
              0.0,
              1.0
            ],
            [
              10.0,
              82.0,
              0.0,
              12.0
            ]
          ],
          "audio": "audio/demo_latest/physwave/demo_04_dog_barking_approach_recede.wav"
        },
        {
          "id": "demo_04_dog_barking_circular",
          "trajectoryKey": "circular",
          "trajectoryLabel": "Circular",
          "prompt": "dog bark circling from front-left around the listener to rear-right.",
          "spatialPhrase": "circling from front-left around the listener to rear-right",
          "waypoints": [
            [
              0.0,
              55.0,
              0.0,
              3.0
            ],
            [
              1.25,
              76.875,
              0.0,
              3.0
            ],
            [
              2.5,
              98.75,
              0.0,
              3.0
            ],
            [
              3.75,
              120.625,
              0.0,
              3.0
            ],
            [
              5.0,
              142.5,
              0.0,
              3.0
            ],
            [
              6.25,
              164.375,
              0.0,
              3.0
            ],
            [
              7.5,
              -173.75,
              0.0,
              3.0
            ],
            [
              8.75,
              -151.875,
              0.0,
              3.0
            ],
            [
              10.0,
              -130.0,
              0.0,
              3.0
            ]
          ],
          "audio": "audio/demo_latest/physwave/demo_04_dog_barking_circular.wav"
        }
      ]
    },
    {
      "event": "telephone ringing",
      "basePrompt": "telephone ringing",
      "variants": [
        {
          "id": "demo_05_telephone_ringing_static",
          "trajectoryKey": "static",
          "trajectoryLabel": "Static",
          "prompt": "telephone ringing stationary at the right side.",
          "spatialPhrase": "stationary at the right side",
          "waypoints": [
            [
              0.0,
              -92.0,
              -10.0,
              1.6
            ],
            [
              10.0,
              -92.0,
              -10.0,
              1.6
            ]
          ],
          "audio": "audio/demo_latest/physwave/demo_05_telephone_ringing_static.wav"
        },
        {
          "id": "demo_05_telephone_ringing_linear",
          "trajectoryKey": "linear",
          "trajectoryLabel": "Linear",
          "prompt": "telephone ringing moving in a straight line from the right side to the front.",
          "spatialPhrase": "moving in a straight line from the right side to the front",
          "waypoints": [
            [
              0.0,
              -90.0,
              0.0,
              2.0
            ],
            [
              1.25,
              -81.999,
              0.0,
              1.789
            ],
            [
              2.5,
              -72.116,
              0.0,
              1.622
            ],
            [
              3.75,
              -60.403,
              0.0,
              1.513
            ],
            [
              5.0,
              -47.5,
              0.0,
              1.475
            ],
            [
              6.25,
              -34.597,
              0.0,
              1.513
            ],
            [
              7.5,
              -22.884,
              0.0,
              1.622
            ],
            [
              8.75,
              -13.001,
              0.0,
              1.789
            ],
            [
              10.0,
              -5.0,
              0.0,
              2.0
            ]
          ],
          "audio": "audio/demo_latest/physwave/demo_05_telephone_ringing_linear.wav"
        },
        {
          "id": "demo_05_telephone_ringing_approach_recede",
          "trajectoryKey": "approach_recede",
          "trajectoryLabel": "Approach / Recede",
          "prompt": "telephone ringing approaching from far away to nearby on the front-right.",
          "spatialPhrase": "approaching from far away to nearby on the front-right",
          "waypoints": [
            [
              0.0,
              -35.0,
              0.0,
              9.5
            ],
            [
              10.0,
              -35.0,
              0.0,
              1.0
            ]
          ],
          "audio": "audio/demo_latest/physwave/demo_05_telephone_ringing_approach_recede.wav"
        },
        {
          "id": "demo_05_telephone_ringing_circular",
          "trajectoryKey": "circular",
          "trajectoryLabel": "Circular",
          "prompt": "telephone ringing circling from front-right to the rear-left.",
          "spatialPhrase": "circling from front-right to the rear-left",
          "waypoints": [
            [
              0.0,
              -45.0,
              0.0,
              2.8
            ],
            [
              1.25,
              -67.5,
              0.0,
              2.8
            ],
            [
              2.5,
              -90.0,
              0.0,
              2.8
            ],
            [
              3.75,
              -112.5,
              0.0,
              2.8
            ],
            [
              5.0,
              -135.0,
              0.0,
              2.8
            ],
            [
              6.25,
              -157.5,
              0.0,
              2.8
            ],
            [
              7.5,
              -180.0,
              0.0,
              2.8
            ],
            [
              8.75,
              157.5,
              0.0,
              2.8
            ],
            [
              10.0,
              135.0,
              0.0,
              2.8
            ]
          ],
          "audio": "audio/demo_latest/physwave/demo_05_telephone_ringing_circular.wav"
        }
      ]
    },
    {
      "event": "horn",
      "basePrompt": "car horn",
      "variants": [
        {
          "id": "demo_06_horn_static",
          "trajectoryKey": "static",
          "trajectoryLabel": "Static",
          "prompt": "car horn stationary on the right, above ear level.",
          "spatialPhrase": "stationary on the right, above ear level",
          "waypoints": [
            [
              0.0,
              -110.0,
              35.0,
              1.1
            ],
            [
              10.0,
              -110.0,
              35.0,
              1.1
            ]
          ],
          "audio": "audio/demo_latest/physwave/demo_06_horn_static.wav"
        },
        {
          "id": "demo_06_horn_linear",
          "trajectoryKey": "linear",
          "trajectoryLabel": "Linear",
          "prompt": "car horn moving in a straight line from the front-left side to the front.",
          "spatialPhrase": "moving in a straight line from the front-left side to the front",
          "waypoints": [
            [
              0.0,
              60.0,
              0.0,
              1.4
            ],
            [
              1.25,
              52.183,
              0.0,
              1.267
            ],
            [
              2.5,
              42.76,
              0.0,
              1.163
            ],
            [
              3.75,
              31.847,
              0.0,
              1.096
            ],
            [
              5.0,
              20.0,
              0.0,
              1.072
            ],
            [
              6.25,
              8.153,
              0.0,
              1.096
            ],
            [
              7.5,
              -2.76,
              0.0,
              1.163
            ],
            [
              8.75,
              -12.183,
              0.0,
              1.267
            ],
            [
              10.0,
              -20.0,
              0.0,
              1.4
            ]
          ],
          "audio": "audio/demo_latest/physwave/demo_06_horn_linear.wav"
        },
        {
          "id": "demo_06_horn_approach_recede",
          "trajectoryKey": "approach_recede",
          "trajectoryLabel": "Approach / Recede",
          "prompt": "car horn receding from close front-left to far front-left.",
          "spatialPhrase": "receding from close front-left to far front-left",
          "waypoints": [
            [
              0.0,
              45.0,
              -10.0,
              1.0
            ],
            [
              10.0,
              45.0,
              -10.0,
              11.0
            ]
          ],
          "audio": "audio/demo_latest/physwave/demo_06_horn_approach_recede.wav"
        },
        {
          "id": "demo_06_horn_circular",
          "trajectoryKey": "circular",
          "trajectoryLabel": "Circular",
          "prompt": "car horn circling on the right side from front-right to rear-right.",
          "spatialPhrase": "circling on the right side from front-right to rear-right",
          "waypoints": [
            [
              0.0,
              -35.0,
              0.0,
              2.4
            ],
            [
              1.25,
              -48.75,
              0.0,
              2.4
            ],
            [
              2.5,
              -62.5,
              0.0,
              2.4
            ],
            [
              3.75,
              -76.25,
              0.0,
              2.4
            ],
            [
              5.0,
              -90.0,
              0.0,
              2.4
            ],
            [
              6.25,
              -103.75,
              0.0,
              2.4
            ],
            [
              7.5,
              -117.5,
              0.0,
              2.4
            ],
            [
              8.75,
              -131.25,
              0.0,
              2.4
            ],
            [
              10.0,
              -145.0,
              0.0,
              2.4
            ]
          ],
          "audio": "audio/demo_latest/physwave/demo_06_horn_circular.wav"
        }
      ]
    },
    {
      "event": "engine idling",
      "basePrompt": "engine idling",
      "variants": [
        {
          "id": "demo_07_engine_idling_static",
          "trajectoryKey": "static",
          "trajectoryLabel": "Static",
          "prompt": "engine idling stationary at the rear-right, above ear level.",
          "spatialPhrase": "stationary at the rear-right, above ear level",
          "waypoints": [
            [
              0.0,
              -120.0,
              20.0,
              2.0
            ],
            [
              10.0,
              -120.0,
              20.0,
              2.0
            ]
          ],
          "audio": "audio/demo_latest/physwave/demo_07_engine_idling_static.wav"
        },
        {
          "id": "demo_07_engine_idling_linear",
          "trajectoryKey": "linear",
          "trajectoryLabel": "Linear",
          "prompt": "engine idling moving in a straight line from the front-right to the rear-right.",
          "spatialPhrase": "moving in a straight line from the front-right to the rear-right",
          "waypoints": [
            [
              0.0,
              -60.0,
              20.0,
              1.5
            ],
            [
              1.25,
              -67.817,
              21.906,
              1.375
            ],
            [
              2.5,
              -77.24,
              23.66,
              1.278
            ],
            [
              3.75,
              -88.153,
              24.939,
              1.217
            ],
            [
              5.0,
              -100.0,
              25.414,
              1.195
            ],
            [
              6.25,
              -111.847,
              24.939,
              1.217
            ],
            [
              7.5,
              -122.76,
              23.66,
              1.278
            ],
            [
              8.75,
              -132.183,
              21.906,
              1.375
            ],
            [
              10.0,
              -140.0,
              20.0,
              1.5
            ]
          ],
          "audio": "audio/demo_latest/physwave/demo_07_engine_idling_linear.wav"
        },
        {
          "id": "demo_07_engine_idling_approach_recede",
          "trajectoryKey": "approach_recede",
          "trajectoryLabel": "Approach / Recede",
          "prompt": "engine idling approaching from far behind to close behind.",
          "spatialPhrase": "approaching from far behind to close behind",
          "waypoints": [
            [
              0.0,
              175.0,
              0.0,
              14.0
            ],
            [
              10.0,
              175.0,
              0.0,
              1.4
            ]
          ],
          "audio": "audio/demo_latest/physwave/demo_07_engine_idling_approach_recede.wav"
        },
        {
          "id": "demo_07_engine_idling_circular",
          "trajectoryKey": "circular",
          "trajectoryLabel": "Circular",
          "prompt": "engine idling circling slowly from rear-right to front-left.",
          "spatialPhrase": "circling slowly from rear-right to front-left",
          "waypoints": [
            [
              0.0,
              -135.0,
              10.0,
              3.5
            ],
            [
              1.25,
              -156.25,
              10.0,
              3.5
            ],
            [
              2.5,
              -177.5,
              10.0,
              3.5
            ],
            [
              3.75,
              161.25,
              10.0,
              3.5
            ],
            [
              5.0,
              140.0,
              10.0,
              3.5
            ],
            [
              6.25,
              118.75,
              10.0,
              3.5
            ],
            [
              7.5,
              97.5,
              10.0,
              3.5
            ],
            [
              8.75,
              76.25,
              10.0,
              3.5
            ],
            [
              10.0,
              55.0,
              10.0,
              3.5
            ]
          ],
          "audio": "audio/demo_latest/physwave/demo_07_engine_idling_circular.wav"
        }
      ]
    }
  ]
};
