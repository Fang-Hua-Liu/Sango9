from battle_engine import (
    Arms,
    BattleContext,
    Formation,
    Officer,
    Terrain,
    Unit,
    calculate_damage,
    tactic_success_rate,
)


def demo() -> None:
    zhao_yun = Officer(name="趙雲", leadership=92, might=94, intelligence=76)
    yuan_shao_general = Officer(name="顏良", leadership=83, might=90, intelligence=58)

    attacker = Unit(
        officer=zhao_yun,
        troops=5000,
        arms=Arms.CAVALRY,
        formation=Formation.FENGSHI,
        morale=88,
    )
    defender = Unit(
        officer=yuan_shao_general,
        troops=5300,
        arms=Arms.BOW,
        formation=Formation.YULIN,
        morale=74,
    )

    ctx = BattleContext(terrain=Terrain.PLAIN, is_siege_target=False, random_factor=1.0)
    dmg = calculate_damage(attacker, defender, ctx)
    rate = tactic_success_rate(zhao_yun.intelligence, yuan_shao_general.intelligence)

    print(f"{attacker.officer.name} 對 {defender.officer.name} 預估傷害: {dmg}")
    print(f"戰法成功率(趙雲->顏良): {rate:.1f}%")


if __name__ == "__main__":
    demo()
