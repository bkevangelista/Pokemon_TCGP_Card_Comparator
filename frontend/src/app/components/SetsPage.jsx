"use client";

import apiRoutes from "@/app/utils/apiRoutes"

import Image from "next/image";
import { useState, useEffect, useRef } from "react";
import Select from "react-select"

import { RARITY_CONSTANTS } from "@/app/constants/constants";

export default function SetPage() {
    const [tcgpSets, setTCGPSets] = useState([]);
    const [userName, setUserName] = useState("");
    const [selectedSet, setSelectedSet] = useState("");
    const [cards, setCards] = useState([]);
    const [loadingCards, setLoadingCards] = useState(false);
    const [currentPage, setCurrentPage] = useState(1);
    const [userCards, setUserCards] = useState([]);

    const cardsPerPage = 25;

    const indexOfLastCard = currentPage * cardsPerPage;
    const indexOfFirstCard = indexOfLastCard - cardsPerPage;
    const currentCards = cards.slice(indexOfFirstCard, indexOfLastCard);
    const totalPages = Math.ceil(cards.length / cardsPerPage);

    const tableContainerRef = useRef(null);

    useEffect(() => {
        if (tableContainerRef.current) {
            tableContainerRef.current.scrollTo({ top: 0, behavior: "smooth" });
        }
    }, [currentPage]);

    useEffect(() => {
        const fetchSets = async () => {
            try {
                const res = await fetch(apiRoutes.getSets);
                const data = await res.json();

                const sets = data.tcgSets;

                const setOptions = sets.map(s => ({
                   value: s.set_id,
                   label: s.set_name
                }));

                setTCGPSets(setOptions);
            } catch (err) {
                console.error("Error fetching set names: ", err);
            }

        }
        fetchSets();
    }, []);

    const initializeUserCards = (cards) => {
        const initialUserCards = [];
        cards.forEach(card => {
            initialUserCards.push({
                user_id: userName,
                card_id: card.id,
                set_id: card.set_id,
                no_owned: 0
            });
        });
        setUserCards(initialUserCards);
    };

    const fetchCards = async (setId) => {
        setLoadingCards(true);
        try {
            const res = await fetch(apiRoutes.getCards(setId));
            const data = await res.json();
            setCards(data.cards)

            // Initialize the user cards state variable
            initializeUserCards(data.cards)
        } catch (err) {
            console.error(`Error fetching cards of set id ${setId}: `, err);
        } finally {
            setLoadingCards(false);
        }
    };

    const handleSetChange = (e) => {
        const setId = e.value;
        setSelectedSet(setId);
        setCurrentPage(1);

        if (setId) {
            fetchCards(setId);
        } else {
            setCards([]);
        }
    };

    const handleUserNameChange = (e) => {
        const user = e.target.value;
        setUserName(user)

        if (!user) {
            setSelectedSet("");
            setCards([]);
            setUserCards([]);
        }
    };

    const handleUserCardsChange = (e, index) => {
        const value = parseInt(e.target.value, 10) || 0;
        setUserCards(prev => {
            const updated = [...prev];
            updated[index] = { ...updated[index], no_owned: value };
            return updated;
        });
    };

    const handleSubmit = async () => {
        const payload = { cards: userCards };

        try {
            const res = await fetch(apiRoutes.addUserCards, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const data = await res.json();
            console.log(data.message);
        } catch (err) {
            console.error("Could not insert user cards: ", err);
        }
    };

    return (
        <div>
            <h1 className="flex justify-center">Select a Pokémon TCGP Set</h1>
            <div className="flex justify-center m-4">
                <input
                    type="text"
                    value={userName}
                    onChange={handleUserNameChange}
                    placeholder="Enter username"
                    className="border rounded px-3 py-2 w-64"
                    required
                />
            </div>

            {userName && (
                <div className="flex justify-center">
                    <div className="inline-block m-4">
                        <Select
                            options={tcgpSets}
                            onChange={handleSetChange}
                            styles={{
                                container: (provided) => ({
                                    ...provided,
                                    width: "auto", // shrink-to-fit
                                    minWidth: "fit-content",
                                }),
                                control: (provided) => ({
                                    ...provided,
                                    backgroundColor: "white",
                                    color: "black",
                                    width: "auto", // let content dictate width
                                    minWidth: "fit-content",
                                }),
                                option: (provided) => ({
                                    ...provided,
                                    color: "black",
                                    backgroundColor: "white",
                                })
                        }}
                        />
                    </div>
                </div>
            )}

            {loadingCards ? (
                <p className="flex justify-center">Loading Cards</p>
            ) : (
                (userName && selectedSet && userCards) && (
                    <div ref={tableContainerRef} className="max-w-4xl max-h-[600px] mx-auto overflow-y-auto mt-6 border-4 border-black rounded-lg shadow-lg bg-white">
                        <table className="w-full table-auto border-collapse border-gray-300 bg-white text-black rounded-lg overflow-hidden">
                            <thead className="bg-purple-500 text-white">
                                <tr>
                                    <th className="px-4 py-2 border border-gray-300">Number</th>
                                    <th className="px-4 py-2 border border-gray-300">Image</th>
                                    <th className="px-4 py-2 border border-gray-300">Name</th>
                                    <th className="px-4 py-2 border border-gray-300">Rarity</th>
                                    <th className="px-4 py-2 border border-gray-300">Quantity Owned</th>
                                </tr>
                            </thead>
                            <tbody>
                            {currentCards.map((card, index) => (
                                <tr key={card.id} className="hover:bg-gray-100">
                                    <td className="px-4 py-2 border border-gray-300">{card.local_id}</td>
                                    <td className="px-4 py-2 border border-gray-300">
                                        <Image
                                            src={`${card.image}/low.png`}
                                            alt={card.name}
                                            width={100}
                                            height={140}
                                            className="object-contain"
                                        />
                                    </td>
                                    <td className="px-4 py-2 border border-gray-300">{card.name}</td>
                                    <td className="px-4 py-2 border border-gray-300">
                                        {card.rarity && (
                                            <Image
                                                src={RARITY_CONSTANTS?.[card.rarity]}
                                                alt={card.rarity}
                                                width={100}
                                                height={140}
                                                className="object-contain"
                                            />
                                        )}
                                    </td>
                                    <td className="px-4 py-2 border border-gray-300">
                                        <input
                                            type="number"
                                            min="0"
                                            value={userCards[(currentPage - 1) * cardsPerPage + index]?.["no_owned"]}
                                            onChange={(e) => handleUserCardsChange(e, (currentPage - 1) * cardsPerPage + index)}
                                            className="w-20 border rounded px-2 py-1"
                                        />
                                    </td>
                                </tr>
                            ))}
                            </tbody>
                        </table>

                        {totalPages > 1 && (
                            <div className="flex justify-center items-center mt-4 gap-2">
                                <button
                                    onClick={() => setCurrentPage((prev) => prev - 1)}
                                    disabled={currentPage === 1}
                                    className={`my-2 px-4 py-2 rounded-lg font-bold tracking-wider border-4 border-black shadow-lg transform transition
                                    ${currentPage === 1 
                                        ? "bg-gray-400 text-gray-700 cursor-not-allowed" 
                                        : "bg-gradient-to-b from-yellow-300 to-yellow-500 hover:scale-105 hover:from-yellow-400 hover:to-yellow-600"
                                    }`}
                                >
                                    ◀ Prev
                                </button>
                                <span className="px-3 py-1 text-black">
                                    Page {currentPage} of {totalPages}
                                </span>
                                <button
                                    onClick={() => setCurrentPage((prev) => prev + 1)}
                                    disabled={currentPage === totalPages}
                                    className={`my-2 px-4 py-2 rounded-lg font-bold tracking-wider border-4 border-black shadow-lg transform transition
                                    ${currentPage === totalPages
                                        ? "bg-gray-400 text-gray-700 cursor-not-allowed"
                                        : "bg-gradient-to-b from-yellow-300 to-yellow-500 hover:scale-105 hover:from-yellow-400 hover:to-yellow-600"
                                    }`}
                                >
                                    Next ▶
                                </button>
                            </div>
                        )}
                    </div>
                )
            )}

            {(userName && selectedSet && userCards) && (
                <div className="flex justify-center items-center mt-4 gap-2">
                    <button
                        onClick={handleSubmit}
                        className="px-4 py-2 bg-gradient-to-b from-yellow-300 to-yellow-500 hover:scale-105 hover:from-yellow-400 hover:to-yellow-600 transition"
                    >
                        Submit Cards
                    </button>
                </div>
            )}
        </div>
    );
}
