import Foundation

struct StandingsService {
    enum ServiceError: LocalizedError {
        case invalidResponse
        case decodingFailed

        var errorDescription: String? {
            switch self {
            case .invalidResponse:
                return "The server returned an unexpected response."
            case .decodingFailed:
                return "We couldn't parse the latest standings data."
            }
        }
    }

    private let session: URLSession
    private let baseURL = URL(string: "https://statsapi.mlb.com/api/v1/standings")!

    init(session: URLSession = .shared) {
        self.session = session
    }

    func fetchStandings(season: Int, leagueIds: [Int] = [103, 104]) async throws -> StandingsResponse {
        var components = URLComponents(url: baseURL, resolvingAgainstBaseURL: false)!
        components.queryItems = [
            URLQueryItem(name: "leagueId", value: leagueIds.map(String.init).joined(separator: ",")),
            URLQueryItem(name: "season", value: String(season)),
            URLQueryItem(name: "standingsTypes", value: "regularSeason"),
            URLQueryItem(name: "hydrate", value: "team,league,division"),
            URLQueryItem(name: "fields", value: fieldsQuery)
        ]

        guard let url = components.url else {
            throw ServiceError.invalidResponse
        }

        let (data, response) = try await session.data(from: url)

        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            throw ServiceError.invalidResponse
        }

        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase

        do {
            return try decoder.decode(StandingsResponse.self, from: data)
        } catch {
            throw ServiceError.decodingFailed
        }
    }

    private var fieldsQuery: String {
        [
            "records",
            "records.teamRecords",
            "records.teamRecords.team",
            "records.teamRecords.streak",
            "records.teamRecords.divisionRank",
            "records.teamRecords.leagueRank",
            "records.teamRecords.wildCardRank",
            "records.teamRecords.wins",
            "records.teamRecords.losses",
            "records.teamRecords.winningPercentage",
            "records.teamRecords.gamesBack",
            "records.teamRecords.runsScored",
            "records.teamRecords.runsAllowed",
            "records.teamRecords.runDifferential",
            "records.teamRecords.lastTen",
            "records.teamRecords.home",
            "records.teamRecords.away",
            "records.teamRecords.extraInnings",
            "records.teamRecords.oneRun",
            "records.teamRecords.clinched",
            "records.league",
            "records.division",
            "records.season"
        ].joined(separator: ",")
    }
}
