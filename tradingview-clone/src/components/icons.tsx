export function LogoIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 120 28"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M8 24V4h4v20H8zM14 24V4h4v20h-4zM20 24V4h4v20h-4zM0 24V4h4v20H0zM26 24V4h4v20h-4z"
        fill="#2962FF"
      />
      <text x="36" y="20" fill="#f7f8f8" fontSize="16" fontWeight="700" fontFamily="Arial">
        TradingView
      </text>
    </svg>
  );
}

export function SearchIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 28 28" fill="none">
      <path
        d="M13 5a8 8 0 105.3 14.1l4.3 4.3a1 1 0 001.4-1.4l-4.3-4.3A8 8 0 0013 5zm0 2a6 6 0 110 12 6 6 0 010-12z"
        fill="currentColor"
      />
    </svg>
  );
}

export function GlobeIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 28 28" fill="none">
      <path
        d="M14 3a11 11 0 100 22 11 11 0 000-22zm0 2a9 9 0 018.7 6.5H5.3A9 9 0 0114 5zm-9 9c0-.7.1-1.4.3-2h17.4c.2.6.3 1.3.3 2s-.1 1.4-.3 2H5.3a9 9 0 01-.3-2zm1.1 4h15.8a9 9 0 01-15.8 0z"
        fill="currentColor"
      />
    </svg>
  );
}

export function UserIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 28 28" fill="none">
      <path
        d="M14 4a5 5 0 100 10 5 5 0 000-10zm0 2a3 3 0 110 6 3 3 0 010-6zM6 23c0-3.3 3.6-6 8-6s8 2.7 8 6v1H6v-1z"
        fill="currentColor"
      />
    </svg>
  );
}

export function ArrowRightIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 16 16" fill="none">
      <path
        d="M5.5 2.5L11 8l-5.5 5.5"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function ArrowUpIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 10 10" fill="currentColor">
      <path d="M5 0l5 10H0z" />
    </svg>
  );
}

export function ArrowDownIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 10 10" fill="currentColor">
      <path d="M5 10L0 0h10z" />
    </svg>
  );
}

export function StarIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 16 16" fill="none">
      <path
        d="M8 1l1.8 5.5H15l-4.5 3.3 1.7 5.2L8 12l-4.2 3 1.7-5.2L1 6.5h5.2L8 1z"
        fill="currentColor"
      />
    </svg>
  );
}

export function ChartIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 16 16" fill="none">
      <rect x="1" y="10" width="3" height="5" rx="0.5" fill="currentColor" />
      <rect x="6.5" y="5" width="3" height="10" rx="0.5" fill="currentColor" />
      <rect x="12" y="1" width="3" height="14" rx="0.5" fill="currentColor" />
    </svg>
  );
}

export function TrendingUpIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
      <polyline points="17 6 23 6 23 12" />
    </svg>
  );
}

export function ExternalLinkIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 16 16" fill="none">
      <path d="M12 8.5V13a1 1 0 01-1 1H3a1 1 0 01-1-1V5a1 1 0 011-1h4.5M10 2h4v4M9 7l4.5-4.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
