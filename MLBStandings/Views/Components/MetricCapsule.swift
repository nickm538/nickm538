import SwiftUI

struct MetricCapsule: View {
    let title: String
    let value: String
    let subtitle: String
    let systemImage: String
    let gradient: LinearGradient

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: systemImage)
                    .font(.system(size: 18, weight: .semibold))
                Spacer()
                Text(title.uppercased())
                    .font(.caption)
                    .fontWeight(.semibold)
                    .tracking(1.4)
                    .foregroundStyle(.white.opacity(0.7))
            }

            Text(value)
                .font(.system(size: 32, weight: .bold, design: .rounded))
                .minimumScaleFactor(0.7)
                .foregroundStyle(.white)

            Text(subtitle)
                .font(.footnote)
                .foregroundStyle(.white.opacity(0.85))
        }
        .padding(20)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: 24, style: .continuous)
                .fill(gradient)
                .shadow(color: .black.opacity(0.18), radius: 18, x: 0, y: 12)
        )
        .overlay(
            RoundedRectangle(cornerRadius: 24, style: .continuous)
                .stroke(Color.white.opacity(0.2), lineWidth: 1)
        )
    }
}

struct MetricCapsule_Previews: PreviewProvider {
    static var previews: some View {
        MetricCapsule(
            title: "Best Record",
            value: "Dodgers",
            subtitle: "0.699 Win %",
            systemImage: "trophy.fill",
            gradient: TeamBranding.palette(for: "LAD").gradient
        )
        .padding()
        .background(Color.black.opacity(0.9))
    }
}
