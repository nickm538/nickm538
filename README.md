# MLBStandings — Interactive MLB Standings for iOS

MLBStandings is a modern SwiftUI application that brings the latest Major League Baseball standings to your iPhone or iPad. The experience blends live data from the MLB Stats API with a refined, glassmorphism-inspired interface that makes digging into division battles, momentum swings, and situational splits feel cinematic and fast.

https://github.com/user-attachments/assets/8c2179c3-f8f4-4d0e-bb67-66c725131ac2

## Highlights

- **Dynamic dashboards** – Explore league and division standings with rich cards, adaptive gradients, and at-a-glance power rankings.
- **Powerful filtering** – Instantly narrow the board with text search, league toggles, division chips, and advanced sorting (win %, run differential, streaks, last 10, and more).
- **Team detail deep dives** – Tap any club to surface a richly branded sheet with split records, momentum analysis, and contextual metrics.
- **Favorites mode** – Star your must-watch teams and bubble them to the top of every list.
- **Seasons on demand** – Jump between any season from 2018 to the present with one tap. Pull-to-refresh keeps the board current.

## Project structure

```
MLBStandings/
├─ MLBStandings.xcodeproj        // Xcode project for the SwiftUI app
├─ MLBStandingsApp.swift         // Entry point that wires the shared view model
├─ Models/                       // Decodable API models + domain transformations
├─ ViewModels/                   // `StandingsViewModel` with filtering/sorting logic
├─ Services/                     // `StandingsService` (Stats API client)
├─ Views/                        // Dashboard, sections, detail sheet, reusable UI
├─ Utilities/                    // Color helpers and styling utilities
└─ Resources/                    // Assets catalog & Info.plist
```

### Technology choices
- **SwiftUI (iOS 16+)** for a declarative UI, custom gradients, and modern animations.
- **Async/await URLSession** to stream standings from the public MLB Stats API.
- **ObservableObject architecture** with a single `StandingsViewModel` that powers the dashboard, filters, and detail sheet.
- **Brand-driven design** using custom palettes for each MLB franchise and glassmorphism cards to keep focus on data.

## Getting started

1. Open `MLBStandings/MLBStandings.xcodeproj` in Xcode 15 or later.
2. Select the `MLBStandings` scheme and target an iOS 16+ simulator or device.
3. Build & run (⌘+R). The app fetches live data on launch and supports pull-to-refresh.

> The build has no third-party dependencies and uses the default `com.example.MLBStandings` bundle identifier—swap it for your team ID before signing to a device.

## Roadmap ideas
- Live tiles for league leaders (HR, OPS, ERA) alongside the standings board.
- Notification hooks when a favorite club changes playoff positioning.
- WidgetKit support for lock-screen & home screen tiles.

Enjoy tracking the pennant race! ⚾️
