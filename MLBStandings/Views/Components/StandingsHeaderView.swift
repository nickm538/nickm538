import SwiftUI

struct StandingsHeaderView: View {
    let season: Int
    let bestTeam: TeamStanding?
    let hottestTeam: TeamStanding?
    let topRunDifferentialTeam: TeamStanding?

    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            VStack(alignment: .leading, spacing: 6) {
                Text("MLB Standings")
                    .font(.system(size: 34, weight: .bold, design: .rounded))
                    .foregroundStyle(.white)
                Text("Season \(season)")
                    .font(.title3.weight(.semibold))
                    .foregroundStyle(.white.opacity(0.75))
            }

            VStack(spacing: 16) {
                if let bestTeam {
                    MetricCapsule(
                        title: "Best Record",
                        value: bestTeam.shortName,
                        subtitle: "\(bestTeam.winningPercentageText) Win %",
                        systemImage: "trophy.fill",
                        gradient: bestTeam.branding.gradient
                    )
                }

                HStack(spacing: 16) {
                    if let hottestTeam {
                        MetricCapsule(
                            title: "Hottest Team",
                            value: hottestTeam.shortName,
                            subtitle: "Streak \(hottestTeam.streakDescription)",
                            systemImage: "flame.fill",
                            gradient: hottestTeam.branding.subtleGradient
                        )
                    }

                    if let topRunDifferentialTeam {
                        MetricCapsule(
                            title: "Run Differential",
                            value: topRunDifferentialTeam.shortName,
                            subtitle: topRunDifferentialTeam.runDifferentialText,
                            systemImage: "chart.bar.fill",
                            gradient: topRunDifferentialTeam.branding.subtleGradient
                        )
                    }
                }
                .frame(maxWidth: .infinity)
            }
        }
        .padding(24)
        .background(
            RoundedRectangle(cornerRadius: 32, style: .continuous)
                .fill(.ultraThinMaterial)
                .overlay(
                    RoundedRectangle(cornerRadius: 32, style: .continuous)
                        .stroke(.white.opacity(0.18), lineWidth: 1)
                )
                .shadow(color: .black.opacity(0.25), radius: 20, x: 0, y: 14)
        )
    }
}

struct StandingsHeaderView_Previews: PreviewProvider {
    static var previews: some View {
        StandingsHeaderView(
            season: 2024,
            bestTeam: .sample,
            hottestTeam: .sample,
            topRunDifferentialTeam: .sample
        )
        .padding()
        .background(LinearGradient(colors: [.black, .blue], startPoint: .top, endPoint: .bottom))
    }
}
