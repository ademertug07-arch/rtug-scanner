import NavBar from "@/components/NavBar"
import HeroSection from "@/components/HeroSection"
import MarketOverview from "@/components/MarketOverview"
import IPOSection from "@/components/IPOSection"
import CommunityIdeas from "@/components/CommunityIdeas"
import ScriptsList from "@/components/ScriptsList"
import TurkishStocks from "@/components/TurkishStocks"
import Footer from "@/components/Footer"

export default function Home() {
  return (
    <>
      <NavBar />
      <main>
        <HeroSection />
        <MarketOverview />
        <IPOSection />
        <CommunityIdeas />
        <ScriptsList />
        <TurkishStocks />
      </main>
      <Footer />
    </>
  )
}
