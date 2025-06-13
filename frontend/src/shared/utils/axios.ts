// ---------------------------------------------------------------------------------
// Legacy alias: provide a drop-in replacement for the previous axios instance while
// internally delegating to the new BaseAPI compatibility client (apiClient). This
// keeps existing component imports (e.g. `import axios from '../../utils/axios';`)
// working without any code changes.
// ---------------------------------------------------------------------------------

import apiClient from './apiClient';

export default apiClient;
