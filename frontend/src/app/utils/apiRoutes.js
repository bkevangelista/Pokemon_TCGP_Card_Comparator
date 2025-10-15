const API_URL = process.env.NEXT_PUBLIC_API_URL

const apiRoutes = {
    getSets: `${API_URL}/external/tcg/getSets`,
    getCards: (setId) =>
        `${API_URL}/external/tcg/getCards?set_id=${setId}`,
    addUserCards: `${API_URL}/external/tcg/addUserCards`,
    compareCardsForUsersToTrade: (userOne, userTwo, setId) =>
        `${API_URL}/external/tcg/compareCardsForUsersToTrade?user1=${userOne}&user2=${userTwo}&set_id=${setId}`,
};

export default apiRoutes;