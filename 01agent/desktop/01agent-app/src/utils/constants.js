const constants = {
  API_BASE_URL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8001',
  API_KEY: process.env.REACT_APP_API_KEY,
  APP_NAME: '01Agent',
  AGENT_LINK: 'https://www.get01agent.com',
  GENERAL_ERROR: 'Something wrong happened, please try again.',
  status: {
    INTERNAL_SERVER_ERROR: 500,
    BAD_REQUEST: 400,
    UNAUTHORIZED: 401,
    FORBIDDEN: 403,
    NOT_FOUND: 404,
    CONFLICT: 409,
    UNPROCESSABLE_ENTITY: 422,
    TOO_MANY_REQUESTS: 429,
    OK: 200,
    CREATED: 201,
    NO_CONTENT: 204
  }
};

export default constants;