import SwiftUI

struct TeamRowView: View {
    let team: TeamStanding
    let isFavorite: Bool
    let onFavoriteToggle: () -> Void
    let onSelect: () -> Void

    var body: some View {
        VStack(spacing: 0) {
            HStack(alignment: .center, spacing: 16) {
                ZStack {
                    Circle()
                        .fill(team.branding.gradient)
                        .frame(width: 58, height: 58)
                        .shadow(color: team.branding.primary.opacity(0.35), radius: 10, x: 0, y: 8)
                    Text(team.abbreviation)
                        .font(.system(size: 20, weight: .bold, design: .rounded))
                        .foregroundStyle(team.branding.textColor)
                }

                VStack(alignment: .leading, spacing: 6) {
                    HStack(alignment: .firstTextBaseline) {
                        Text(team.shortName)
                            .font(.system(size: 20, weight: .semibold, design: .rounded))
                            .foregroundStyle(.primary)
                        if team.clinched {
                            Label("Clinched", systemImage: "checkmark.seal.fill")
                                .font(.caption)
                                .foregroundStyle(.green)
                                .padding(.horizontal, 8)
                                .padding(.vertical, 4)
                                .background(
                                    Capsule(style: .continuous)
                                        .fill(Color.green.opacity(0.18))
                                )
                        }
                    }

                    HStack(spacing: 14) {
                        labelView(title: team.recordText, systemImage: "sportscourt")
                        labelView(title: team.winningPercentageText, systemImage: "percent")
                        labelView(title: team.gamesBackText, systemImage: "arrow.triangle.branch")
                    }
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                }

                Spacer(minLength: 12)

                VStack(alignment: .trailing, spacing: 6) {
                    Text(team.runDifferentialText)
                        .font(.system(size: 18, weight: .semibold, design: .rounded))
                        .foregroundStyle(team.runDifferential ?? 0 >= 0 ? Color.green : Color.red)
                    Text("Streak \(team.streakDescription)")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    Text("Last 10: \(team.lastTenRecord)")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }

                Button(action: onFavoriteToggle) {
                    Image(systemName: isFavorite ? "star.fill" : "star")
                        .font(.system(size: 18, weight: .semibold))
                        .foregroundStyle(isFavorite ? Color.yellow : Color.secondary)
                }
                .buttonStyle(.plain)
            }
            .padding(20)
            .background(
                RoundedRectangle(cornerRadius: 28, style: .continuous)
                    .fill(Color.white.opacity(0.9))
                    .overlay(
                        RoundedRectangle(cornerRadius: 28, style: .continuous)
                            .stroke(team.branding.primary.opacity(0.15), lineWidth: 1)
                    )
                    .shadow(color: team.branding.primary.opacity(0.12), radius: 16, x: 0, y: 10)
            )
            .contentShape(Rectangle())
            .onTapGesture { onSelect() }
        }
    }

    private func labelView(title: String, systemImage: String) -> some View {
        HStack(spacing: 4) {
            Image(systemName: systemImage)
            Text(title)
        }
        .padding(.horizontal, 8)
        .padding(.vertical, 6)
        .background(
            Capsule(style: .continuous)
                .fill(Color.secondary.opacity(0.12))
        )
        .foregroundStyle(.secondary)
    }
}

struct TeamRowView_Previews: PreviewProvider {
    static var previews: some View {
        VStack(spacing: 24) {
            TeamRowView(team: .sample, isFavorite: true, onFavoriteToggle: {}, onSelect: {})
            TeamRowView(team: StandingsSection.sample[1].teams[2], isFavorite: false, onFavoriteToggle: {}, onSelect: {})
        }
        .padding()
        .background(Color(UIColor.systemGroupedBackground))
    }
}
