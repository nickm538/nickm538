import SwiftUI

struct StandingsSectionView: View {
    let section: StandingsSection
    let favorites: Set<Int>
    let onFavoriteToggle: (TeamStanding) -> Void
    let onTeamSelected: (TeamStanding) -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 18) {
            HStack(alignment: .firstTextBaseline) {
                Text(section.title)
                    .font(.system(size: 26, weight: .bold, design: .rounded))
                    .foregroundStyle(.white)
                Spacer()
                Text(section.leagueAbbreviation)
                    .font(.headline)
                    .foregroundStyle(.white.opacity(0.7))
                    .padding(.horizontal, 12)
                    .padding(.vertical, 6)
                    .background(
                        Capsule(style: .continuous)
                            .fill(.white.opacity(0.15))
                    )
            }

            VStack(spacing: 16) {
                ForEach(section.teams) { team in
                    TeamRowView(
                        team: team,
                        isFavorite: favorites.contains(team.id),
                        onFavoriteToggle: { onFavoriteToggle(team) },
                        onSelect: { onTeamSelected(team) }
                    )
                }
            }
        }
        .padding(24)
        .background(
            RoundedRectangle(cornerRadius: 36, style: .continuous)
                .fill(
                    LinearGradient(
                        colors: [Color.black.opacity(0.55), Color.black.opacity(0.35)],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
                .overlay(
                    RoundedRectangle(cornerRadius: 36, style: .continuous)
                        .stroke(.white.opacity(0.1), lineWidth: 1)
                )
                .shadow(color: .black.opacity(0.25), radius: 30, x: 0, y: 24)
        )
    }
}

struct StandingsSectionView_Previews: PreviewProvider {
    static var previews: some View {
        ScrollView {
            StandingsSectionView(
                section: StandingsSection.sample[0],
                favorites: Set([147]),
                onFavoriteToggle: { _ in },
                onTeamSelected: { _ in }
            )
            .padding()
        }
        .background(LinearGradient(colors: [.blue, .black], startPoint: .topLeading, endPoint: .bottomTrailing))
    }
}
