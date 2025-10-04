import SwiftUI

struct TeamDetailView: View {
    let team: TeamStanding
    let isFavorite: Bool
    let onFavoriteToggle: () -> Void

    var body: some View {
        ScrollView {
            VStack(spacing: 24) {
                header
                statsOverview
                if team.homeRecord != nil || team.awayRecord != nil {
                    splitSection
                }
                streakSection
            }
            .padding(.vertical, 24)
            .padding(.horizontal, 20)
        }
        .background(LinearGradient(colors: [Color.black, Color.blue.opacity(0.6)], startPoint: .top, endPoint: .bottom).ignoresSafeArea())
    }

    private var header: some View {
        VStack(spacing: 16) {
            HStack(alignment: .center) {
                VStack(alignment: .leading, spacing: 8) {
                    Text(team.location.uppercased())
                        .font(.caption)
                        .foregroundStyle(.white.opacity(0.75))
                        .tracking(2)
                    Text(team.shortName)
                        .font(.system(size: 34, weight: .bold, design: .rounded))
                        .foregroundStyle(.white)
                    Text("Record \(team.recordText) • Win % \(team.winningPercentageText)")
                        .font(.headline)
                        .foregroundStyle(.white.opacity(0.8))
                }
                Spacer()
                VStack(spacing: 12) {
                    Circle()
                        .fill(team.branding.gradient)
                        .frame(width: 82, height: 82)
                        .overlay(
                            Text(team.abbreviation)
                                .font(.system(size: 28, weight: .bold, design: .rounded))
                                .foregroundStyle(team.branding.textColor)
                        )
                    favoriteButton
                }
            }

            HStack(spacing: 16) {
                detailMetric(title: "Division Rank", value: formattedRank(team.divisionRank))
                detailMetric(title: "League Rank", value: formattedRank(team.leagueRank))
                detailMetric(title: "Wild Card", value: formattedRank(team.wildCardRank))
            }
        }
        .padding(24)
        .background(
            RoundedRectangle(cornerRadius: 36, style: .continuous)
                .fill(team.branding.gradient)
                .overlay(
                    RoundedRectangle(cornerRadius: 36, style: .continuous)
                        .stroke(.white.opacity(0.2), lineWidth: 1)
                )
                .shadow(color: team.branding.primary.opacity(0.35), radius: 24, x: 0, y: 18)
        )
    }

    private var statsOverview: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Advanced Snapshot")
                .font(.title2.weight(.bold))
                .foregroundStyle(.white)

            LazyVGrid(columns: [GridItem(.adaptive(minimum: 140), spacing: 16)], spacing: 16) {
                statTile(title: "Run Differential", value: team.runDifferentialText, icon: "waveform.path.ecg")
                statTile(title: "Runs Scored", value: "\(team.runsScored ?? 0)", icon: "chart.bar.xaxis")
                statTile(title: "Runs Allowed", value: "\(team.runsAllowed ?? 0)", icon: "shield.lefthalf.fill")
                statTile(title: "Games Back", value: team.gamesBackText, icon: "arrow.left.arrow.right")
                statTile(title: "Last 10", value: team.lastTenRecord, icon: "number.square")
                statTile(title: "Streak", value: team.streakDescription, icon: "flame")
            }
        }
        .padding(24)
        .background(
            RoundedRectangle(cornerRadius: 32, style: .continuous)
                .fill(.ultraThinMaterial)
                .overlay(
                    RoundedRectangle(cornerRadius: 32, style: .continuous)
                        .stroke(.white.opacity(0.12), lineWidth: 1)
                )
        )
    }

    private var splitSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Situational Splits")
                .font(.title2.weight(.bold))
                .foregroundStyle(.white)
            Text("Understand how the \(team.shortName) fare in different game states.")
                .font(.subheadline)
                .foregroundStyle(.white.opacity(0.75))

            VStack(spacing: 14) {
                if let homeRecord = team.homeRecord {
                    splitRow(title: "Home", record: homeRecord, icon: "house.fill")
                }
                if let awayRecord = team.awayRecord {
                    splitRow(title: "Away", record: awayRecord, icon: "airplane.departure")
                }
                if let oneRun = team.oneRunRecord {
                    splitRow(title: "One-Run Games", record: oneRun, icon: "heart.circle")
                }
                if let extras = team.extraInningsRecord {
                    splitRow(title: "Extra Innings", record: extras, icon: "clock.arrow.circlepath")
                }
            }
        }
        .padding(24)
        .background(
            RoundedRectangle(cornerRadius: 32, style: .continuous)
                .fill(Color.white.opacity(0.08))
                .overlay(
                    RoundedRectangle(cornerRadius: 32, style: .continuous)
                        .stroke(.white.opacity(0.1), lineWidth: 1)
                )
        )
    }

    private var streakSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Momentum")
                .font(.title2.weight(.bold))
                .foregroundStyle(.white)
            Text("The current streak tells the story of their latest run of form.")
                .font(.subheadline)
                .foregroundStyle(.white.opacity(0.75))

            VStack(alignment: .leading, spacing: 10) {
                Text("Streak: \(team.streakDescription)")
                    .font(.headline)
                    .foregroundStyle(team.streakIsWin ? Color.green : Color.red)
                Text("Win % over last 10: \(String(format: "%.0f%%", team.lastTenWinRate * 100))")
                    .foregroundStyle(.white.opacity(0.8))
                Text("Games back: \(team.gamesBackText)")
                    .foregroundStyle(.white.opacity(0.8))
            }
            .padding()
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(
                RoundedRectangle(cornerRadius: 24, style: .continuous)
                    .fill(team.branding.subtleGradient)
                    .overlay(
                        RoundedRectangle(cornerRadius: 24, style: .continuous)
                            .stroke(.white.opacity(0.2), lineWidth: 1)
                    )
            )
        }
        .padding(24)
        .background(
            RoundedRectangle(cornerRadius: 32, style: .continuous)
                .fill(.ultraThinMaterial)
                .overlay(
                    RoundedRectangle(cornerRadius: 32, style: .continuous)
                        .stroke(.white.opacity(0.12), lineWidth: 1)
                )
        )
    }

    private var favoriteButton: some View {
        Button {
            onFavoriteToggle()
        } label: {
            Label(isFavorite ? "Favorited" : "Add Favorite", systemImage: isFavorite ? "star.fill" : "star")
                .font(.subheadline.weight(.semibold))
                .padding(.horizontal, 12)
                .padding(.vertical, 8)
                .background(
                    Capsule(style: .continuous)
                        .fill(Color.white.opacity(0.22))
                )
                .foregroundStyle(isFavorite ? Color.yellow : Color.white)
        }
        .buttonStyle(.plain)
    }

    private func detailMetric(title: String, value: String) -> some View {
        VStack(spacing: 8) {
            Text(title.uppercased())
                .font(.caption)
                .foregroundStyle(.white.opacity(0.7))
                .tracking(1.2)
            Text(value)
                .font(.title3.weight(.semibold))
                .foregroundStyle(.white)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 20, style: .continuous)
                .fill(Color.white.opacity(0.15))
        )
    }

    private func statTile(title: String, value: String, icon: String) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Image(systemName: icon)
                .font(.system(size: 20, weight: .semibold))
                .foregroundStyle(.white.opacity(0.8))
            Text(value)
                .font(.title.bold())
                .foregroundStyle(.white)
            Text(title)
                .font(.subheadline)
                .foregroundStyle(.white.opacity(0.8))
        }
        .padding(18)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: 24, style: .continuous)
                .fill(Color.white.opacity(0.1))
        )
    }

    private func splitRow(title: String, record: RecordSplit, icon: String) -> some View {
        HStack {
            Label(title, systemImage: icon)
                .font(.headline)
                .foregroundStyle(.white)
            Spacer()
            Text(record.formatted)
                .font(.system(size: 18, weight: .bold, design: .rounded))
                .foregroundStyle(.white)
            Text(String(format: "%.3f", record.percentage))
                .font(.subheadline)
                .foregroundStyle(.white.opacity(0.75))
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 20, style: .continuous)
                .fill(Color.white.opacity(0.08))
        )
    }

    private func formattedRank(_ rank: Int?) -> String {
        guard let rank else { return "—" }
        switch rank % 10 {
        case 1 where rank != 11: return "\(rank)st"
        case 2 where rank != 12: return "\(rank)nd"
        case 3 where rank != 13: return "\(rank)rd"
        default: return "\(rank)th"
        }
    }
}

struct TeamDetailView_Previews: PreviewProvider {
    static var previews: some View {
        TeamDetailView(team: .sample, isFavorite: true, onFavoriteToggle: {})
            .preferredColorScheme(.dark)
    }
}
