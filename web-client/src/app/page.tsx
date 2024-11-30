'use client'
import DropDown from "@/components/DropDown";
import GeneralButton from "@/components/GeneralButton";
import { useState } from "react";
import { League, Model } from "@/utils/types";
import { LEAGUES, MODELS } from "@/utils/constants";
import Table from "@/components/Table";

export default function Home() {
  const [selectedModel, setSelectedModel] = useState<Model | null>(null);
  const [selectedLeague, setSelectedLeague] = useState<League | null>(null);
  const [trainText, setTrainText] = useState<string>("Train Models");
  const [scrapeText, setScrapeText] = useState<string>("Scrape Data");

  const getPredictions = (league: string, model: string) => {

  }

  const handleModelSelect = (selectedItem: Model) => {
    // console.log(selectedItem)
    setSelectedModel(selectedItem);
  };

  const handleLeagueSelect = (selectedItem: League) => {
    // console.log(selectedItem)
    setSelectedLeague(selectedItem);
  }

  const handleScrape = () => {
    const fetchData = async () => {
      let intervalId: NodeJS.Timeout | null = null;
      try {
        // Start dynamic loading animation
        const scrapingTexts = ["Scraping.", "Scraping..", "Scraping..."];
        let textIndex = 0;

        intervalId = setInterval(() => {
          setScrapeText(scrapingTexts[textIndex]);
          textIndex = (textIndex + 1) % scrapingTexts.length;
        }, 500); // Change text every 500ms

        const response = await fetch('http://127.0.0.1:8080/api/scrape');
        // const response = await fetch('http://127.0.0.1:8080/api/test');
        const responseData = await response.json();
        // console.log(responseData.message);
      } catch (error) {
        console.error('Error scraping data: ', error);
      } finally {
        if (intervalId) clearInterval(intervalId); // Stop the interval
        setScrapeText("Scrape Data"); // Reset button text
      }
    };
    fetchData();
  }

  const handleTrain = () => {
    const fetchData = async () => {
      let intervalId: NodeJS.Timeout | null = null;
      try {
        // Start dynamic loading animation
        const trainingTexts = ["Training.", "Training..", "Training..."];
        let textIndex = 0;

        intervalId = setInterval(() => {
          setTrainText(trainingTexts[textIndex]);
          textIndex = (textIndex + 1) % trainingTexts.length;
        }, 500); // Change text every 500ms

          const response = await fetch('http://127.0.0.1:8080/api/train-and-predict');
          // const response = await fetch('http://127.0.0.1:8080/api/test');
          const responseData = await response.json();
          // console.log(responseData.message);
      } catch (error) {
          console.error('Error fetching data: ', error);
      } finally {
        if (intervalId) clearInterval(intervalId); // Stop the interval
        setTrainText("Train Models"); // Reset button text
      }
    };
    fetchData();
  }

  return (
    <div className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <div className="flex w-full justify-between items-center">
        <div className="font-semibold text-5xl">Soccer-Match-Predictor</div>

        <div className="flex gap-24 items-center">
          <GeneralButton primary size="m" buttonClick={handleScrape}>
            {scrapeText}
          </GeneralButton>
          <GeneralButton primary size="m" buttonClick={handleTrain}>
            {trainText}
          </GeneralButton>
          <DropDown items={LEAGUES} onSelect={handleLeagueSelect} text="Select League" />
          <DropDown items={MODELS} onSelect={handleModelSelect} text="Select Model" />
        </div>
      </div>
      <main className="flex flex-col gap-8 row-start-2 items-center sm:items-start">
        <Table league={selectedLeague} model={selectedModel}/>
      </main>
      <footer className="row-start-3 flex gap-6 flex-wrap items-center justify-center">
        {/* FOOTER */}
      </footer>
    </div>
  );
}
