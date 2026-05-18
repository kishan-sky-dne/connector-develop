# """
# __author__ = "Sky UK Ltd"
# __copyright__ = Copyright © Sky CP Limited 2023.
# All rights reserved. No part of this work may be reproduced,
# stored in a retrieval system of any nature, or transmitted,
# in any form or by any means including photocopying
# and recording, without the prior written permission of Sky,
# the copyright owner.
# __licence__ = "subject to the terms of the licence with Sky UK Ltd'
# __version__ = "1.0"
# """
## ADMIN DATABASE Scripts


#### Admin DB has two scripts
1.  software_lifecycle_management.sql
    -   This script needs to be execute first to create all the necessary tables and data.
2.  traffic_diversion_script.sql
    -   This script should be execute after the `software_lifecycle_management.sql` script. This script create the necessary procudure and triggers to insert/update into `traffic_diversion` table.

After execute both the scripts there will be two procudures created:
1.  `insert_update_into_traffic_diversion`
    -   To insert or update the traffic diversion table.
    -   e.g. `call insert_update_into_traffic_diversion('UK', 'NCS5K', 'SUPER CORE', 'ISIS', 'Off', 1, 0, null);`
2.  `delete_from_traffic_diversion`
    -   To delete form traffict divesrion table.
    -   `call software_lifecycle_management.delete_from_traffic_diversion('UK', 'NCS5K', 'SUPER CORE', 'ISIS', 'Off', 1);`