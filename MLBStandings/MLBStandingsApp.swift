import SwiftUI

@main
struct MLBStandingsApp: App {
    @StateObject private var viewModel = StandingsViewModel()

    var body: some Scene {
        WindowGroup {
            StandingsDashboardView()
                .environmentObject(viewModel)
        }
    }
}
