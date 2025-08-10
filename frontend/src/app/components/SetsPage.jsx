"use client";

import { useState, useEffect } from "react";

export default function SetPage() {
  const [tcgpSets, setTCGPSets] = useState([]);

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/external/tcg/getSets`)
      .then(res => res.json())
      .then(data => setTCGPSets(data.tcgSets));
  }, []);

  return (
    <div>
      <h1>All Sets</h1>
      <ul>
        {tcgpSets.map((set) => (
          <li key={set.set_id}>{`${set.set_name} - ${set.set_id}`}</li>
        ))}
      </ul>
    </div>
  );
}
