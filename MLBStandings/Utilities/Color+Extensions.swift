import SwiftUI
import UIKit

extension Color {
    init(hex: String, alpha: Double = 1.0) {
        let sanitized = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: sanitized).scanHexInt64(&int)
        let r, g, b: UInt64
        switch sanitized.count {
        case 3: // RGB (12-bit)
            (r, g, b) = ((int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
        case 6: // RGB (24-bit)
            (r, g, b) = (int >> 16, int >> 8 & 0xFF, int & 0xFF)
        default:
            (r, g, b) = (26, 66, 142)
        }

        self.init(
            .sRGB,
            red: Double(r) / 255.0,
            green: Double(g) / 255.0,
            blue: Double(b) / 255.0,
            opacity: alpha
        )
    }

    var uiColor: UIColor {
        UIColor(self)
    }

    func luminance() -> Double {
        let components = uiColor.cgColor.components ?? [0, 0, 0, 1]
        let red = Double(components[0])
        let green = Double(components[min(1, components.count - 1)])
        let blue = Double(components[min(2, components.count - 1)])

        func adjust(_ component: Double) -> Double {
            return component <= 0.03928 ? component / 12.92 : pow(((component + 0.055) / 1.055), 2.4)
        }

        let r = adjust(red)
        let g = adjust(green)
        let b = adjust(blue)

        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    }

    func contrastingTextColor() -> Color {
        luminance() > 0.5 ? .black : .white
    }
}
