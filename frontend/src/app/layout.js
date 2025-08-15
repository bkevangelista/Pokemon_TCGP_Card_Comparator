import { Geist, Geist_Mono } from "next/font/google";
import localFont from "next/font/local";
import "./globals.css";

const pokemonFont = localFont({
    src: "./fonts/PokemonGb-font.ttf",
    variable: "--font-pokemon"
});

export const metadata = {
  title: "TCGP Card Comparator",
  description: "TCGP Card Comparator",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body
        className={`${pokemonFont.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
