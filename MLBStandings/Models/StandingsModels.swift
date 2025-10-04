import Foundation
import SwiftUI

struct StandingsResponse: Decodable {
    let records: [DivisionRecord]
}

struct DivisionRecord: Decodable {
    let teamRecords: [TeamRecord]
    let division: DivisionInfo?
    let league: LeagueInfo?
    let season: String?
}

struct DivisionInfo: Decodable {
    let id: Int
    let name: String
    let nameShort: String?
    let abbreviation: String?
    let shortName: String?
}

struct LeagueInfo: Decodable {
    let id: Int
    let name: String
    let abbreviation: String?
}

struct TeamRecord: Decodable {
    struct Streak: Decodable {
        let streakCode: String?
        let streakNumber: Int?
        let streakType: String?
    }

    struct Split: Decodable {
        let wins: Int?
        let losses: Int?
        let pct: String?
    }

    let team: TeamInfo
    let streak: Streak?
    let divisionRank: String?
    let leagueRank: String?
    let wildCardRank: String?
    let clinched: Bool?

    let wins: Int
    let losses: Int
    let winningPercentage: String
    let gamesBack: String?

    let runsScored: Int?
    let runsAllowed: Int?
    let runDifferential: Int?

    let lastTen: String?
    let home: Split?
    let away: Split?
    let extraInnings: Split?
    let oneRun: Split?
}

struct TeamInfo: Decodable {
    let id: Int
    let name: String
    let teamName: String?
    let shortName: String?
    let clubName: String?
    let locationName: String?
    let abbreviation: String?
    let fileCode: String?
}

struct RecordSplit: Hashable {
    let wins: Int
    let losses: Int
    let percentage: Double

    var formatted: String {
        "\(wins)-\(losses)"
    }

    init(wins: Int, losses: Int, percentage: Double) {
        self.wins = wins
        self.losses = losses
        self.percentage = percentage
    }

    init?(split: TeamRecord.Split?) {
        guard let wins = split?.wins, let losses = split?.losses else { return nil }
        self.init(wins: wins, losses: losses, percentage: Double(split?.pct) ?? 0)
    }
}

struct StandingsSection: Identifiable, Hashable {
    let id: Int
    let divisionID: Int
    let leagueID: Int
    let leagueName: String
    let leagueAbbreviation: String
    let title: String
    let subtitle: String
    var teams: [TeamStanding]
    let season: Int

    init(from record: DivisionRecord) {
        let leagueId = record.league?.id ?? 0
        self.leagueID = leagueId
        self.leagueName = record.league?.name ?? "Major League Baseball"

        let derivedAbbreviation: String
        if let explicit = record.league?.abbreviation {
            derivedAbbreviation = explicit
        } else if leagueName.localizedCaseInsensitiveContains("American") {
            derivedAbbreviation = "AL"
        } else if leagueName.localizedCaseInsensitiveContains("National") {
            derivedAbbreviation = "NL"
        } else {
            derivedAbbreviation = "MLB"
        }
        self.leagueAbbreviation = derivedAbbreviation

        let divisionId = record.division?.id ?? (leagueId * 100 + 1)
        self.divisionID = divisionId
        self.title = record.division?.name ?? leagueName
        self.subtitle = record.division?.shortName ?? record.division?.nameShort ?? record.league?.name ?? ""
        let mappedSeason = Int(record.season ?? "") ?? StandingsViewModel.currentSeason
        self.season = mappedSeason

        self.teams = record.teamRecords.map { TeamStanding(record: $0, league: record.league, division: record.division, season: mappedSeason) }
        self.id = divisionId
    }

    init(id: Int, divisionID: Int, leagueID: Int, leagueName: String, leagueAbbreviation: String, title: String, subtitle: String, teams: [TeamStanding], season: Int) {
        self.id = id
        self.divisionID = divisionID
        self.leagueID = leagueID
        self.leagueName = leagueName
        self.leagueAbbreviation = leagueAbbreviation
        self.title = title
        self.subtitle = subtitle
        self.teams = teams
        self.season = season
    }
}

struct TeamStanding: Identifiable, Hashable {
    let id: Int
    let name: String
    let shortName: String
    let location: String
    let abbreviation: String
    let wins: Int
    let losses: Int
    let winningPercentage: Double
    let winningPercentageText: String
    let gamesBack: Double?
    let gamesBackText: String
    let runDifferential: Int?
    let runsScored: Int?
    let runsAllowed: Int?
    let divisionRank: Int?
    let leagueRank: Int?
    let wildCardRank: Int?
    let streakCode: String
    let streakCount: Int
    let streakIsWin: Bool
    let lastTenRecord: String
    let lastTenWinRate: Double
    let clinched: Bool
    let homeRecord: RecordSplit?
    let awayRecord: RecordSplit?
    let extraInningsRecord: RecordSplit?
    let oneRunRecord: RecordSplit?
    let branding: TeamBranding
    let season: Int
    let leagueID: Int
    let divisionID: Int

    init(record: TeamRecord, league: LeagueInfo?, division: DivisionInfo?, season: Int) {
        let team = record.team
        self.id = team.id
        self.name = team.name
        self.shortName = team.shortName ?? team.teamName ?? team.name
        self.location = team.locationName ?? team.name
        self.abbreviation = team.abbreviation ?? String(team.name.prefix(3)).uppercased()
        self.wins = record.wins
        self.losses = record.losses

        let percentageValue = Double(record.winningPercentage) ?? 0
        self.winningPercentage = percentageValue
        self.winningPercentageText = String(format: "%.3f", percentageValue)

        let gamesBackValue = Double(record.gamesBack)
        self.gamesBack = gamesBackValue
        if let gamesBackValue {
            self.gamesBackText = gamesBackValue == 0 ? "—" : String(format: "%.1f GB", gamesBackValue)
        } else {
            self.gamesBackText = record.gamesBack ?? "—"
        }

        self.runDifferential = record.runDifferential
        self.runsScored = record.runsScored
        self.runsAllowed = record.runsAllowed

        self.divisionRank = Int(record.divisionRank ?? "")
        self.leagueRank = Int(record.leagueRank ?? "")
        self.wildCardRank = Int(record.wildCardRank ?? "")

        let streakCode = record.streak?.streakCode ?? ""
        self.streakCode = streakCode.isEmpty ? Self.defaultStreakCode(from: record.streak) : streakCode
        self.streakCount = record.streak?.streakNumber ?? Int(streakCode.dropFirst()) ?? 0
        let isWin = record.streak?.streakType?.lowercased() == "wins" || streakCode.uppercased().hasPrefix("W")
        self.streakIsWin = isWin

        let lastTen = record.lastTen ?? "0-0"
        self.lastTenRecord = lastTen
        self.lastTenWinRate = TeamStanding.winRate(from: lastTen)

        self.clinched = record.clinched ?? false

        self.homeRecord = RecordSplit(split: record.home)
        self.awayRecord = RecordSplit(split: record.away)
        self.extraInningsRecord = RecordSplit(split: record.extraInnings)
        self.oneRunRecord = RecordSplit(split: record.oneRun)

        self.branding = TeamBranding.palette(for: self.abbreviation)
        self.season = season
        self.leagueID = league?.id ?? 0
        self.divisionID = division?.id ?? 0
    }

    var recordText: String {
        "\(wins)-\(losses)"
    }

    var runDifferentialText: String {
        guard let runDifferential else { return "—" }
        return (runDifferential >= 0 ? "+" : "") + "\(runDifferential)"
    }

    var streakDescription: String {
        guard streakCount > 0 else { return "—" }
        let prefix = streakIsWin ? "W" : "L"
        return "\(prefix)\(streakCount)"
    }

    var searchableText: String {
        [name, shortName, location, abbreviation].joined(separator: " ").lowercased()
    }

    static func defaultStreakCode(from streak: TeamRecord.Streak?) -> String {
        guard let streak else { return "" }
        let number = streak.streakNumber ?? 0
        let prefix = (streak.streakType ?? "").lowercased() == "wins" ? "W" : "L"
        return "\(prefix)\(number)"
    }

    static func winRate(from record: String) -> Double {
        let components = record.split(separator: "-")
        guard components.count == 2,
              let wins = Double(components[0]),
              let losses = Double(components[1]) else { return 0 }
        let total = wins + losses
        guard total > 0 else { return 0 }
        return wins / total
    }

    static let sample = TeamStanding(
        id: 147,
        name: "New York Yankees",
        shortName: "Yankees",
        location: "New York",
        abbreviation: "NYY",
        wins: 62,
        losses: 30,
        winningPercentage: 0.674,
        winningPercentageText: "0.674",
        gamesBack: 0,
        gamesBackText: "—",
        runDifferential: 126,
        runsScored: 432,
        runsAllowed: 306,
        divisionRank: 1,
        leagueRank: 1,
        wildCardRank: nil,
        streakCode: "W4",
        streakCount: 4,
        streakIsWin: true,
        lastTenRecord: "8-2",
        lastTenWinRate: 0.8,
        clinched: false,
        homeRecord: RecordSplit(wins: 35, losses: 14, percentage: 0.714),
        awayRecord: RecordSplit(wins: 27, losses: 16, percentage: 0.628),
        extraInningsRecord: RecordSplit(wins: 5, losses: 2, percentage: 0.714),
        oneRunRecord: RecordSplit(wins: 12, losses: 8, percentage: 0.600),
        branding: TeamBranding.palette(for: "NYY"),
        season: 2024,
        leagueID: 103,
        divisionID: 201
    )

    private init(id: Int, name: String, shortName: String, location: String, abbreviation: String, wins: Int, losses: Int, winningPercentage: Double, winningPercentageText: String, gamesBack: Double?, gamesBackText: String, runDifferential: Int?, runsScored: Int?, runsAllowed: Int?, divisionRank: Int?, leagueRank: Int?, wildCardRank: Int?, streakCode: String, streakCount: Int, streakIsWin: Bool, lastTenRecord: String, lastTenWinRate: Double, clinched: Bool, homeRecord: RecordSplit?, awayRecord: RecordSplit?, extraInningsRecord: RecordSplit?, oneRunRecord: RecordSplit?, branding: TeamBranding, season: Int, leagueID: Int, divisionID: Int) {
        self.id = id
        self.name = name
        self.shortName = shortName
        self.location = location
        self.abbreviation = abbreviation
        self.wins = wins
        self.losses = losses
        self.winningPercentage = winningPercentage
        self.winningPercentageText = winningPercentageText
        self.gamesBack = gamesBack
        self.gamesBackText = gamesBackText
        self.runDifferential = runDifferential
        self.runsScored = runsScored
        self.runsAllowed = runsAllowed
        self.divisionRank = divisionRank
        self.leagueRank = leagueRank
        self.wildCardRank = wildCardRank
        self.streakCode = streakCode
        self.streakCount = streakCount
        self.streakIsWin = streakIsWin
        self.lastTenRecord = lastTenRecord
        self.lastTenWinRate = lastTenWinRate
        self.clinched = clinched
        self.homeRecord = homeRecord
        self.awayRecord = awayRecord
        self.extraInningsRecord = extraInningsRecord
        self.oneRunRecord = oneRunRecord
        self.branding = branding
        self.season = season
        self.leagueID = leagueID
        self.divisionID = divisionID
    }
}

extension StandingsSection {
    static let sample: [StandingsSection] = {
        let yankees = TeamStanding.sample
        let orioles = TeamStanding(
            id: 110,
            name: "Baltimore Orioles",
            shortName: "Orioles",
            location: "Baltimore",
            abbreviation: "BAL",
            wins: 58,
            losses: 35,
            winningPercentage: 0.624,
            winningPercentageText: "0.624",
            gamesBack: 4,
            gamesBackText: "4.0 GB",
            runDifferential: 94,
            runsScored: 421,
            runsAllowed: 327,
            divisionRank: 2,
            leagueRank: 3,
            wildCardRank: 1,
            streakCode: "W2",
            streakCount: 2,
            streakIsWin: true,
            lastTenRecord: "7-3",
            lastTenWinRate: 0.7,
            clinched: false,
            homeRecord: RecordSplit(wins: 30, losses: 18, percentage: 0.625),
            awayRecord: RecordSplit(wins: 28, losses: 17, percentage: 0.622),
            extraInningsRecord: RecordSplit(wins: 4, losses: 1, percentage: 0.800),
            oneRunRecord: RecordSplit(wins: 13, losses: 9, percentage: 0.591),
            branding: TeamBranding.palette(for: "BAL"),
            season: 2024,
            leagueID: 103,
            divisionID: 201
        )

        let rays = TeamStanding(
            id: 139,
            name: "Tampa Bay Rays",
            shortName: "Rays",
            location: "Tampa Bay",
            abbreviation: "TB",
            wins: 53,
            losses: 40,
            winningPercentage: 0.570,
            winningPercentageText: "0.570",
            gamesBack: 9,
            gamesBackText: "9.0 GB",
            runDifferential: 61,
            runsScored: 398,
            runsAllowed: 337,
            divisionRank: 3,
            leagueRank: 6,
            wildCardRank: 2,
            streakCode: "L1",
            streakCount: 1,
            streakIsWin: false,
            lastTenRecord: "6-4",
            lastTenWinRate: 0.6,
            clinched: false,
            homeRecord: RecordSplit(wins: 29, losses: 18, percentage: 0.617),
            awayRecord: RecordSplit(wins: 24, losses: 22, percentage: 0.522),
            extraInningsRecord: RecordSplit(wins: 3, losses: 2, percentage: 0.600),
            oneRunRecord: RecordSplit(wins: 11, losses: 10, percentage: 0.524),
            branding: TeamBranding.palette(for: "TB"),
            season: 2024,
            leagueID: 103,
            divisionID: 201
        )

        let blueJays = TeamStanding(
            id: 141,
            name: "Toronto Blue Jays",
            shortName: "Blue Jays",
            location: "Toronto",
            abbreviation: "TOR",
            wins: 47,
            losses: 46,
            winningPercentage: 0.505,
            winningPercentageText: "0.505",
            gamesBack: 15,
            gamesBackText: "15.0 GB",
            runDifferential: 12,
            runsScored: 372,
            runsAllowed: 360,
            divisionRank: 4,
            leagueRank: 8,
            wildCardRank: 5,
            streakCode: "W1",
            streakCount: 1,
            streakIsWin: true,
            lastTenRecord: "5-5",
            lastTenWinRate: 0.5,
            clinched: false,
            homeRecord: RecordSplit(wins: 25, losses: 21, percentage: 0.543),
            awayRecord: RecordSplit(wins: 22, losses: 25, percentage: 0.468),
            extraInningsRecord: RecordSplit(wins: 2, losses: 3, percentage: 0.400),
            oneRunRecord: RecordSplit(wins: 15, losses: 12, percentage: 0.556),
            branding: TeamBranding.palette(for: "TOR"),
            season: 2024,
            leagueID: 103,
            divisionID: 201
        )

        let redSox = TeamStanding(
            id: 111,
            name: "Boston Red Sox",
            shortName: "Red Sox",
            location: "Boston",
            abbreviation: "BOS",
            wins: 43,
            losses: 52,
            winningPercentage: 0.453,
            winningPercentageText: "0.453",
            gamesBack: 19,
            gamesBackText: "19.0 GB",
            runDifferential: -18,
            runsScored: 360,
            runsAllowed: 378,
            divisionRank: 5,
            leagueRank: 11,
            wildCardRank: 7,
            streakCode: "L2",
            streakCount: 2,
            streakIsWin: false,
            lastTenRecord: "4-6",
            lastTenWinRate: 0.4,
            clinched: false,
            homeRecord: RecordSplit(wins: 19, losses: 27, percentage: 0.413),
            awayRecord: RecordSplit(wins: 24, losses: 25, percentage: 0.490),
            extraInningsRecord: RecordSplit(wins: 1, losses: 4, percentage: 0.200),
            oneRunRecord: RecordSplit(wins: 10, losses: 16, percentage: 0.385),
            branding: TeamBranding.palette(for: "BOS"),
            season: 2024,
            leagueID: 103,
            divisionID: 201
        )

        let alEast = StandingsSection(
            id: 201,
            divisionID: 201,
            leagueID: 103,
            leagueName: "American League",
            leagueAbbreviation: "AL",
            title: "American League East",
            subtitle: "AL East",
            teams: [yankees, orioles, rays, blueJays, redSox],
            season: 2024
        )

        let dodgers = TeamStanding(
            id: 119,
            name: "Los Angeles Dodgers",
            shortName: "Dodgers",
            location: "Los Angeles",
            abbreviation: "LAD",
            wins: 65,
            losses: 28,
            winningPercentage: 0.699,
            winningPercentageText: "0.699",
            gamesBack: 0,
            gamesBackText: "—",
            runDifferential: 154,
            runsScored: 468,
            runsAllowed: 314,
            divisionRank: 1,
            leagueRank: 1,
            wildCardRank: nil,
            streakCode: "W6",
            streakCount: 6,
            streakIsWin: true,
            lastTenRecord: "9-1",
            lastTenWinRate: 0.9,
            clinched: false,
            homeRecord: RecordSplit(wins: 35, losses: 12, percentage: 0.745),
            awayRecord: RecordSplit(wins: 30, losses: 16, percentage: 0.652),
            extraInningsRecord: RecordSplit(wins: 6, losses: 1, percentage: 0.857),
            oneRunRecord: RecordSplit(wins: 18, losses: 9, percentage: 0.667),
            branding: TeamBranding.palette(for: "LAD"),
            season: 2024,
            leagueID: 104,
            divisionID: 203
        )

        let padres = TeamStanding(
            id: 135,
            name: "San Diego Padres",
            shortName: "Padres",
            location: "San Diego",
            abbreviation: "SD",
            wins: 57,
            losses: 37,
            winningPercentage: 0.606,
            winningPercentageText: "0.606",
            gamesBack: 8,
            gamesBackText: "8.0 GB",
            runDifferential: 72,
            runsScored: 420,
            runsAllowed: 348,
            divisionRank: 2,
            leagueRank: 3,
            wildCardRank: 1,
            streakCode: "W3",
            streakCount: 3,
            streakIsWin: true,
            lastTenRecord: "7-3",
            lastTenWinRate: 0.7,
            clinched: false,
            homeRecord: RecordSplit(wins: 29, losses: 18, percentage: 0.617),
            awayRecord: RecordSplit(wins: 28, losses: 19, percentage: 0.596),
            extraInningsRecord: RecordSplit(wins: 4, losses: 2, percentage: 0.667),
            oneRunRecord: RecordSplit(wins: 16, losses: 11, percentage: 0.593),
            branding: TeamBranding.palette(for: "SD"),
            season: 2024,
            leagueID: 104,
            divisionID: 203
        )

        let giants = TeamStanding(
            id: 137,
            name: "San Francisco Giants",
            shortName: "Giants",
            location: "San Francisco",
            abbreviation: "SF",
            wins: 49,
            losses: 45,
            winningPercentage: 0.521,
            winningPercentageText: "0.521",
            gamesBack: 16,
            gamesBackText: "16.0 GB",
            runDifferential: 24,
            runsScored: 390,
            runsAllowed: 366,
            divisionRank: 3,
            leagueRank: 6,
            wildCardRank: 2,
            streakCode: "L1",
            streakCount: 1,
            streakIsWin: false,
            lastTenRecord: "6-4",
            lastTenWinRate: 0.6,
            clinched: false,
            homeRecord: RecordSplit(wins: 27, losses: 22, percentage: 0.551),
            awayRecord: RecordSplit(wins: 22, losses: 23, percentage: 0.489),
            extraInningsRecord: RecordSplit(wins: 3, losses: 3, percentage: 0.500),
            oneRunRecord: RecordSplit(wins: 14, losses: 13, percentage: 0.519),
            branding: TeamBranding.palette(for: "SF"),
            season: 2024,
            leagueID: 104,
            divisionID: 203
        )

        let diamondbacks = TeamStanding(
            id: 109,
            name: "Arizona Diamondbacks",
            shortName: "D-backs",
            location: "Arizona",
            abbreviation: "ARI",
            wins: 46,
            losses: 49,
            winningPercentage: 0.484,
            winningPercentageText: "0.484",
            gamesBack: 19,
            gamesBackText: "19.0 GB",
            runDifferential: -12,
            runsScored: 364,
            runsAllowed: 376,
            divisionRank: 4,
            leagueRank: 8,
            wildCardRank: 5,
            streakCode: "W1",
            streakCount: 1,
            streakIsWin: true,
            lastTenRecord: "5-5",
            lastTenWinRate: 0.5,
            clinched: false,
            homeRecord: RecordSplit(wins: 24, losses: 23, percentage: 0.511),
            awayRecord: RecordSplit(wins: 22, losses: 26, percentage: 0.458),
            extraInningsRecord: RecordSplit(wins: 2, losses: 4, percentage: 0.333),
            oneRunRecord: RecordSplit(wins: 12, losses: 17, percentage: 0.414),
            branding: TeamBranding.palette(for: "ARI"),
            season: 2024,
            leagueID: 104,
            divisionID: 203
        )

        let rockies = TeamStanding(
            id: 115,
            name: "Colorado Rockies",
            shortName: "Rockies",
            location: "Colorado",
            abbreviation: "COL",
            wins: 38,
            losses: 57,
            winningPercentage: 0.400,
            winningPercentageText: "0.400",
            gamesBack: 27,
            gamesBackText: "27.0 GB",
            runDifferential: -92,
            runsScored: 330,
            runsAllowed: 422,
            divisionRank: 5,
            leagueRank: 13,
            wildCardRank: 8,
            streakCode: "L4",
            streakCount: 4,
            streakIsWin: false,
            lastTenRecord: "3-7",
            lastTenWinRate: 0.3,
            clinched: false,
            homeRecord: RecordSplit(wins: 22, losses: 27, percentage: 0.449),
            awayRecord: RecordSplit(wins: 16, losses: 30, percentage: 0.348),
            extraInningsRecord: RecordSplit(wins: 1, losses: 6, percentage: 0.143),
            oneRunRecord: RecordSplit(wins: 9, losses: 21, percentage: 0.300),
            branding: TeamBranding.palette(for: "COL"),
            season: 2024,
            leagueID: 104,
            divisionID: 203
        )

        let nlWest = StandingsSection(
            id: 203,
            divisionID: 203,
            leagueID: 104,
            leagueName: "National League",
            leagueAbbreviation: "NL",
            title: "National League West",
            subtitle: "NL West",
            teams: [dodgers, padres, giants, diamondbacks, rockies],
            season: 2024
        )

        return [alEast, nlWest]
    }()
}

private extension Double {
    init?(_ string: String?) {
        guard let string = string else { return nil }
        let trimmed = string.trimmingCharacters(in: CharacterSet(charactersIn: " %"))
        if trimmed.isEmpty { return nil }
        if trimmed == "—" || trimmed == "-" { return nil }
        if let value = Double(trimmed) {
            self = value
            return
        }
        if let fractional = Double("0" + trimmed) { // handle ".654"
            self = fractional
            return
        }
        return nil
    }
}

private extension Int {
    init?(_ string: String?) {
        guard let string = string else { return nil }
        self.init(string)
    }
}
