"use client";

import apiRoutes from "@/app/utils/apiRoutes"

import Image from "next/image";
import { useState, useEffect } from "react";
import Select from "react-select"

export default function SetPage() {
    const [tcgpSets, setTCGPSets] = useState([]);
    const [selectedSet, setSelectedSet] = useState("");
    const [cards, setCards] = useState([]);
    const [loadingSets, setLoadingSets] = useState(false);
    const [loadingCards, setLoadingCards] = useState(false);

    useEffect(() => {
        const fetchSets = async () => {
            setLoadingSets(true);
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
            } finally {
                setLoadingSets(false);
            }

        }
        fetchSets();
    }, []);

    const fetchCards = async (setId) => {
        setLoadingCards(true);
        try {
            const res = await fetch(apiRoutes.getCards(setId));
            const data = await res.json();
            setCards(data.cards)
        } catch (err) {
            console.error(`Error fetching cards of set id ${setId}: `, err);
        } finally {
            setLoadingCards(false);
        }
    }

    const handleSetChange = (e) => {
        const setId = e.value;
        setSelectedSet(setId);
        if (setId) {
            fetchCards(setId);
        } else {
            setCards([]);
        }
    }

    return (
        <div>
            <h1>Select a Pokémon TCGP Set</h1>
            {loadingSets ? (
                <p>Loading Sets</p>
            ) : (
                <Select options={tcgpSets} onChange={handleSetChange} />
            )}

            {loadingCards ? (
                <p>Loading Cards</p>
            ) : (
                selectedSet && (
                    <ul>
                        {cards.map((card) => (
                            <li key={card.id}>
                                <Image src={`${card.image}/low.png`} alt={card.image} />
                                {card.name} - {card.rarity}
                            </li>
                        ))}
                    </ul>
                )
            )}
        </div>
    );
}
