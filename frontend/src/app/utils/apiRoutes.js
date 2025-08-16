const API_URL = process.env.NEXT_PUBLIC_API_URL

const apiRoutes = {
    getSets: `${API_URL}/external/tcg/getSets`,
    getCards: (setId) =>
        `${API_URL}/external/tcg/getCards?set_id=${setId}`,
    addUserCards: `${API_URL}/external/tcg/addUserCards`
};

export default apiRoutes;