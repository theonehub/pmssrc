import { useMemo } from "react";
import { getToken, getUserRole } from "../utils/auth";

// export const useAuth = () => {
//   const token = getToken();
//   const role = getUserRole();

//   const user = useMemo(() => {
//     if (token && role) {
//       return { role };
//     }
//     return null;
//   }, [token, role]);

//   return { token, user };
// };


// useAuth.js
export const useAuth = () => {
  const token = getToken();
  const role = getUserRole();

  console.log("token in useAuth", token);
  console.log("role in useAuth", role);

  const user = useMemo(() => {
    if (token && role) {
      return { role };
    }
    return null;
  }, [token, role]);

  return { token, user };
};
