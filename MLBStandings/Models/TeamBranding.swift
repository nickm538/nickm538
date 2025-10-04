import SwiftUI

struct TeamBranding: Hashable {
    let abbreviation: String
    let primaryHex: String
    let secondaryHex: String
    let accentHex: String

    var primary: Color { Color(hex: primaryHex) }
    var secondary: Color { Color(hex: secondaryHex) }
    var accent: Color { Color(hex: accentHex) }

    var gradient: LinearGradient {
        LinearGradient(
            colors: [primary, secondary, accent.opacity(0.75)],
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
    }

    var subtleGradient: LinearGradient {
        LinearGradient(
            colors: [primary.opacity(0.9), secondary.opacity(0.8)],
            startPoint: .top,
            endPoint: .bottomTrailing
        )
    }

    var textColor: Color {
        primary.contrastingTextColor()
    }

    var accentTextColor: Color {
        accent.contrastingTextColor()
    }

    static func palette(for abbreviation: String) -> TeamBranding {
        palettes[abbreviation.uppercased()] ?? defaultPalette
    }

    private static let defaultPalette = TeamBranding(
        abbreviation: "MLB",
        primaryHex: "#13274F",
        secondaryHex: "#0C2340",
        accentHex: "#FF6F61"
    )

    private static let palettes: [String: TeamBranding] = [
        "ARI": TeamBranding(abbreviation: "ARI", primaryHex: "#A71930", secondaryHex: "#000000", accentHex: "#E3D4AD"),
        "ATL": TeamBranding(abbreviation: "ATL", primaryHex: "#13274F", secondaryHex: "#CE1141", accentHex: "#EAAA00"),
        "BAL": TeamBranding(abbreviation: "BAL", primaryHex: "#DF4601", secondaryHex: "#000000", accentHex: "#333333"),
        "BOS": TeamBranding(abbreviation: "BOS", primaryHex: "#BD3039", secondaryHex: "#0D2B56", accentHex: "#FFFFFF"),
        "CHC": TeamBranding(abbreviation: "CHC", primaryHex: "#0E3386", secondaryHex: "#CC3433", accentHex: "#FFFFFF"),
        "CHW": TeamBranding(abbreviation: "CHW", primaryHex: "#27251F", secondaryHex: "#C4CED4", accentHex: "#000000"),
        "CIN": TeamBranding(abbreviation: "CIN", primaryHex: "#C6011F", secondaryHex: "#000000", accentHex: "#FFFFFF"),
        "CLE": TeamBranding(abbreviation: "CLE", primaryHex: "#0C2340", secondaryHex: "#E31937", accentHex: "#A4A9AD"),
        "COL": TeamBranding(abbreviation: "COL", primaryHex: "#33006F", secondaryHex: "#C4CED4", accentHex: "#000000"),
        "DET": TeamBranding(abbreviation: "DET", primaryHex: "#0C2340", secondaryHex: "#FA4616", accentHex: "#FFFFFF"),
        "HOU": TeamBranding(abbreviation: "HOU", primaryHex: "#002D62", secondaryHex: "#EB6E1F", accentHex: "#F4911E"),
        "KC": TeamBranding(abbreviation: "KC", primaryHex: "#004687", secondaryHex: "#C09A5B", accentHex: "#FFFFFF"),
        "KCR": TeamBranding(abbreviation: "KCR", primaryHex: "#004687", secondaryHex: "#C09A5B", accentHex: "#FFFFFF"),
        "LAA": TeamBranding(abbreviation: "LAA", primaryHex: "#BA0021", secondaryHex: "#003263", accentHex: "#862633"),
        "LAD": TeamBranding(abbreviation: "LAD", primaryHex: "#005A9C", secondaryHex: "#EF3E42", accentHex: "#FFFFFF"),
        "MIA": TeamBranding(abbreviation: "MIA", primaryHex: "#00A3E0", secondaryHex: "#EF3340", accentHex: "#000000"),
        "MIL": TeamBranding(abbreviation: "MIL", primaryHex: "#0A2351", secondaryHex: "#B6922E", accentHex: "#FFFFFF"),
        "MIN": TeamBranding(abbreviation: "MIN", primaryHex: "#002B5C", secondaryHex: "#D31145", accentHex: "#B9975B"),
        "NYM": TeamBranding(abbreviation: "NYM", primaryHex: "#002D72", secondaryHex: "#FF5910", accentHex: "#FFB81C"),
        "NYN": TeamBranding(abbreviation: "NYN", primaryHex: "#002D72", secondaryHex: "#FF5910", accentHex: "#FFB81C"),
        "NYY": TeamBranding(abbreviation: "NYY", primaryHex: "#0C2340", secondaryHex: "#C4CED4", accentHex: "#A2AAAD"),
        "OAK": TeamBranding(abbreviation: "OAK", primaryHex: "#003831", secondaryHex: "#EFB21E", accentHex: "#A2AAAD"),
        "PHI": TeamBranding(abbreviation: "PHI", primaryHex: "#E81828", secondaryHex: "#002D72", accentHex: "#A7A9AC"),
        "PIT": TeamBranding(abbreviation: "PIT", primaryHex: "#27251F", secondaryHex: "#FDB827", accentHex: "#C4CED4"),
        "SD": TeamBranding(abbreviation: "SD", primaryHex: "#2F241D", secondaryHex: "#FFC425", accentHex: "#0055A5"),
        "SDP": TeamBranding(abbreviation: "SDP", primaryHex: "#2F241D", secondaryHex: "#FFC425", accentHex: "#0055A5"),
        "SEA": TeamBranding(abbreviation: "SEA", primaryHex: "#0C2C56", secondaryHex: "#005C5C", accentHex: "#C4CED4"),
        "SF": TeamBranding(abbreviation: "SF", primaryHex: "#FD5A1E", secondaryHex: "#27251F", accentHex: "#8B6F4E"),
        "STL": TeamBranding(abbreviation: "STL", primaryHex: "#C41E3A", secondaryHex: "#0C2340", accentHex: "#FEDB00"),
        "TB": TeamBranding(abbreviation: "TB", primaryHex: "#092C5C", secondaryHex: "#8FBCE6", accentHex: "#F5D130"),
        "TBR": TeamBranding(abbreviation: "TBR", primaryHex: "#092C5C", secondaryHex: "#8FBCE6", accentHex: "#F5D130"),
        "TEX": TeamBranding(abbreviation: "TEX", primaryHex: "#003278", secondaryHex: "#C0111F", accentHex: "#FFFFFF"),
        "TOR": TeamBranding(abbreviation: "TOR", primaryHex: "#134A8E", secondaryHex: "#1D2D5C", accentHex: "#E8291C"),
        "WSH": TeamBranding(abbreviation: "WSH", primaryHex: "#AB0003", secondaryHex: "#11225B", accentHex: "#FFFFFF"),
        "WSN": TeamBranding(abbreviation: "WSN", primaryHex: "#AB0003", secondaryHex: "#11225B", accentHex: "#FFFFFF"),
        "CWS": TeamBranding(abbreviation: "CWS", primaryHex: "#27251F", secondaryHex: "#C4CED4", accentHex: "#000000")
    ]
}
