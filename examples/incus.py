import plantuml_compose.builders as b

with b.state_diagram(title="Incus Project") as d:
    with d.composite("Provisioning") as c:
        c.arrow(
            c.start(),
            c.state(
                "PXE",
                description="Preboot Execution Environment. Loads embedded linux for next stages",
            ),
            c.state(
                "Load Cloud image",
                description="Embedded 'cloud-deploy' image loads any\ncloud image from upstream vendors (debian in this case)",
            ),
            c.state(
                "Install cloud-init config",
                description="\n".join(["System baseline"]),
            ),
            c.state("Finalize Provisioning"),
        )

print(d.render())
