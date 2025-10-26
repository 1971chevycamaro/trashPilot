import numpy as np

# H = np.array(
#   [[   0.73 ,  -0.,   -167.  ],
#  [   0.,      0.73, -120.  ],
#  [   0. ,     0.  ,    1.  ]], np.float32)
H = np.array(
  [[   0.7 ,  -0.,   150.  ],
 [   0.,      0.7, 150.  ],
 [   0. ,     0.  ,    1.  ]], np.float32)
H = np.linalg.inv(H)