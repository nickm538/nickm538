import Foundation
import SwiftUI

@MainActor
final class StandingsViewModel: ObservableObject {
    @Published private(set) var sections: [StandingsSection] = []
    @Published private(set) var filteredSections: [StandingsSection] = []
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?

    @Published var searchText: String = "" {
        didSet { applyFilters() }
    }

    @Published var selectedLeague: LeagueFilter = .all {
        didSet {
            if let selectedDivisionID, !availableDivisionIDs(for: selectedLeague).contains(selectedDivisionID) {
                self.selectedDivisionID = nil
            }
            applyFilters()
        }
    }

    @Published var selectedDivisionID: Int? = nil {
        didSet { applyFilters() }
    }

    @Published var sortOption: SortOption = .divisionRank {
        didSet { applyFilters() }
    }

    @Published var showFavoritesOnly: Bool = false {
        didSet { applyFilters() }
    }

    @Published var favorites: Set<Int> = [] {
        didSet { applyFilters() }
    }

    @Published var season: Int = StandingsViewModel.currentSeason {
        didSet {
            Task { await loadStandings(force: true) }
        }
    }

    static var currentSeason: Int {
        Calendar.current.component(.year, from: Date())
    }

    static let startSeason: Int = 2018

    let availableSeasons: [Int]

    init(service: StandingsService = StandingsService(), availableSeasons: [Int] = Array((StandingsViewModel.startSeason...StandingsViewModel.currentSeason).reversed())) {
        self.service = service
        self.availableSeasons = availableSeasons

        Task { await loadStandings() }
    }

    func loadStandings(force: Bool = false) async {
        if isLoading { return }
        if !force, !sections.isEmpty { return }

        await MainActor.run {
            isLoading = true
            errorMessage = nil
        }

        do {
            let response = try await service.fetchStandings(season: season)
            let mappedSections = response.records.map { StandingsSection(from: $0) }
            await MainActor.run {
                self.sections = mappedSections
                self.applyFilters()
                self.isLoading = false
            }
        } catch {
            await MainActor.run {
                self.sections = StandingsSection.sample
                self.applyFilters()
                self.errorMessage = error.userFriendlyDescription
                self.isLoading = false
            }
        }
    }

    func refresh() async {
        await loadStandings(force: true)
    }

    func toggleFavorite(for team: TeamStanding) {
        if favorites.contains(team.id) {
            favorites.remove(team.id)
        } else {
            favorites.insert(team.id)
        }
    }

    func clearFilters() {
        searchText = ""
        selectedLeague = .all
        selectedDivisionID = nil
        sortOption = .divisionRank
        showFavoritesOnly = false
    }

    var aggregatedTeams: [TeamStanding] {
        sections.flatMap { $0.teams }
    }

    var bestWinPercentageTeam: TeamStanding? {
        aggregatedTeams.max(by: { $0.winningPercentage < $1.winningPercentage })
    }

    var hottestStreakTeam: TeamStanding? {
        aggregatedTeams.max(by: { $0.streakCount < $1.streakCount })
    }

    var bestRunDifferentialTeam: TeamStanding? {
        aggregatedTeams.max(by: { ($0.runDifferential ?? Int.min) < ($1.runDifferential ?? Int.min) })
    }

    var availableDivisionFilters: [DivisionDescriptor] {
        let leagueFilteredSections: [StandingsSection]
        switch selectedLeague {
        case .all:
            leagueFilteredSections = sections
        case .american:
            leagueFilteredSections = sections.filter { $0.leagueAbbreviation == "AL" }
        case .national:
            leagueFilteredSections = sections.filter { $0.leagueAbbreviation == "NL" }
        }

        var unique: [Int: DivisionDescriptor] = [:]
        for section in leagueFilteredSections {
            unique[section.divisionID] = DivisionDescriptor(id: section.divisionID, name: section.title, leagueAbbreviation: section.leagueAbbreviation)
        }
        return unique.values.sorted(by: { $0.name < $1.name })
    }

    private func applyFilters() {
        var workingSections = sections

        switch selectedLeague {
        case .all:
            break
        case .american:
            workingSections = workingSections.filter { $0.leagueAbbreviation == "AL" }
        case .national:
            workingSections = workingSections.filter { $0.leagueAbbreviation == "NL" }
        }

        if let selectedDivisionID {
            workingSections = workingSections.filter { $0.divisionID == selectedDivisionID }
        }

        workingSections = workingSections.compactMap { section in
            var teams = section.teams

            if showFavoritesOnly {
                teams = teams.filter { favorites.contains($0.id) }
            }

            if !searchText.isEmpty {
                let query = searchText.lowercased()
                teams = teams.filter { team in
                    team.searchableText.contains(query)
                }
            }

            teams = sort(teams: teams)

            guard !teams.isEmpty else { return nil }

            var filteredSection = section
            filteredSection.teams = teams
            return filteredSection
        }

        filteredSections = workingSections
    }

    private func sort(teams: [TeamStanding]) -> [TeamStanding] {
        let comparator: (TeamStanding, TeamStanding) -> Bool
        switch sortOption {
        case .divisionRank:
            comparator = { lhs, rhs in
                (lhs.divisionRank ?? 0) < (rhs.divisionRank ?? 0)
            }
        case .winningPercentage:
            comparator = { lhs, rhs in
                lhs.winningPercentage == rhs.winningPercentage ? (lhs.divisionRank ?? 0) < (rhs.divisionRank ?? 0) : lhs.winningPercentage > rhs.winningPercentage
            }
        case .runDifferential:
            comparator = { lhs, rhs in
                (lhs.runDifferential ?? Int.min) == (rhs.runDifferential ?? Int.min)
                ? (lhs.divisionRank ?? 0) < (rhs.divisionRank ?? 0)
                : (lhs.runDifferential ?? Int.min) > (rhs.runDifferential ?? Int.min)
            }
        case .streak:
            comparator = { lhs, rhs in
                lhs.streakCount == rhs.streakCount ? (lhs.divisionRank ?? 0) < (rhs.divisionRank ?? 0) : lhs.streakCount > rhs.streakCount
            }
        case .lastTen:
            comparator = { lhs, rhs in
                lhs.lastTenWinRate == rhs.lastTenWinRate ? (lhs.divisionRank ?? 0) < (rhs.divisionRank ?? 0) : lhs.lastTenWinRate > rhs.lastTenWinRate
            }
        case .runsScored:
            comparator = { lhs, rhs in
                (lhs.runsScored ?? Int.min) == (rhs.runsScored ?? Int.min)
                ? (lhs.divisionRank ?? 0) < (rhs.divisionRank ?? 0)
                : (lhs.runsScored ?? Int.min) > (rhs.runsScored ?? Int.min)
            }
        }

        let prioritized = teams.sorted(by: { lhs, rhs in
            let lhsFavorite = favorites.contains(lhs.id)
            let rhsFavorite = favorites.contains(rhs.id)
            if lhsFavorite == rhsFavorite { return comparator(lhs, rhs) }
            return lhsFavorite && !rhsFavorite
        })
        return prioritized
    }

    private func availableDivisionIDs(for league: LeagueFilter) -> Set<Int> {
        switch league {
        case .all:
            return Set(sections.map { $0.divisionID })
        case .american:
            return Set(sections.filter { $0.leagueAbbreviation == "AL" }.map { $0.divisionID })
        case .national:
            return Set(sections.filter { $0.leagueAbbreviation == "NL" }.map { $0.divisionID })
        }
    }
}

enum LeagueFilter: String, CaseIterable, Identifiable {
    case all
    case american
    case national

    var id: String { rawValue }

    var title: String {
        switch self {
        case .all: return "All"
        case .american: return "AL"
        case .national: return "NL"
        }
    }
}

enum SortOption: String, CaseIterable, Identifiable {
    case divisionRank
    case winningPercentage
    case runDifferential
    case streak
    case lastTen
    case runsScored

    var id: String { rawValue }

    var title: String {
        switch self {
        case .divisionRank: return "Standings"
        case .winningPercentage: return "Win %"
        case .runDifferential: return "Run Diff"
        case .streak: return "Streak"
        case .lastTen: return "Last 10"
        case .runsScored: return "Runs"
        }
    }

    var systemImage: String {
        switch self {
        case .divisionRank: return "list.number"
        case .winningPercentage: return "percent"
        case .runDifferential: return "plus.slash.minus"
        case .streak: return "flame"
        case .lastTen: return "10.square"
        case .runsScored: return "goforward.plus"
        }
    }
}

struct DivisionDescriptor: Identifiable, Hashable {
    let id: Int
    let name: String
    let leagueAbbreviation: String
}

private extension Error {
    var userFriendlyDescription: String {
        if let error = self as? LocalizedError, let description = error.errorDescription {
            return description
        }
        return (self as NSError).localizedDescription
    }
}
