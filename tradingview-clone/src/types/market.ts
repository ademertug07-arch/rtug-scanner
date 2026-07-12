export interface MarketIndex {
  symbol: string
  name: string
  ticker: string
  price: string
  change: string
  changePercent: string
  unit: string
  isPositive: boolean
  hasGIndicator?: boolean
}

export interface CryptoTicker {
  symbol: string
  name: string
  ticker: string
  price: string
  unit: string
  changePercent: string
  isPositive: boolean
}

export interface DominanceData {
  btcPercent: string
  ethPercent: string
  othersPercent: string
}

export interface CommodityTicker {
  symbol: string
  name: string
  ticker: string
  price: string
  unit: string
  changePercent: string
  isPositive: boolean
  hasGIndicator?: boolean
}

export interface EconomicIndicator {
  name: string
  ticker: string
  value: string
  subValue?: string
  link: string
}

export interface IPOSummary {
  date: string
  symbol: string
  companyName: string
  exchange: string
  lastPrice?: string
  offerPrice?: string
  marketCap?: string
  currency?: string
}

export interface TradingIdea {
  title: string
  description: string
  symbol: string
  symbolLogo: string
  author: string
  authorUrl: string
  date: string
  signal?: "Alış" | "Satış"
  link: string
}

export interface ScriptItem {
  name: string
  description: string
  type: "Pine Script® göstergesi" | "Pine Script® kütüphanesi"
  author: string
  authorUrl: string
  link: string
}

export interface TurkishStock {
  symbol: string
  name: string
  link: string
}

export interface NavLink {
  label: string
  url: string
  hasDropdown: boolean
}
